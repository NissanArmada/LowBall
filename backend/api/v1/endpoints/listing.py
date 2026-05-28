from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from models.schemas import ListingMetadata, NegotiationState, AnalyticalData
from services import vision, scraper, store
from core.config import settings
from core.dependencies import get_store
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

async def background_market_scrape(session_id: str, item_name: str, db: store.SessionStore):
    """
    Background task to perform market scraping and update the session's analytical data.
    Also initiates the first AI greeting to ensure it only happens once.
    """
    from agents import unified
    from models.schemas import Message

    logger.info(f"STARTING background task for session {session_id}")
    try:
        # 1. Perform market analysis
        analytical_res = await scraper.scraper.analyze_market(item_name)
        
        # 2. Load current state
        state = await db.load_state(session_id)
        if not state:
            return

        # 3. Update research data
        state.analytical_data = analytical_res
        
        # 4. Initiate greeting if history is empty (Atomic-ish check)
        if len(state.history) == 0:
            logger.info(f"Session {session_id}: Generating initial AI greeting...")
            # We use a temporary placeholder to prevent other tasks from starting
            state.history.append(Message(role="ai", content="Generating opening line..."))
            await db.save_state(state)
            
            # Real AI call
            response = await unified.get_negotiation_response(state)
            
            # Replace placeholder with real response
            state.history[-1] = Message(role="ai", content=response.final_response)
            state.current_lowball_price = response.suggested_next_price
            
        await db.save_state(state)
        logger.info(f"SUCCESS: Session {session_id} initialized with research and greeting.")
            
    except Exception as e:
        logger.error(f"FAILURE in background task for {session_id}: {str(e)}")

@router.post("/analyze", response_model=ListingMetadata)
async def analyze_listing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: store.SessionStore = Depends(get_store)
):
    """
    Analyzes a screenshot and triggers a persistent background market scrape.
    """
    try:
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large.")

        image_content = await file.read()
        
        if len(image_content) > settings.MAX_FILE_SIZE:
             raise HTTPException(status_code=413, detail="File too large.")

        # 1. Primary Analysis (Vision)
        # vision.analyze_image now returns ItemExtraction
        extraction = await vision.analyze_image(image_content)
        
        # 2. Generate permanent session_id
        session_id = str(uuid.uuid4())
        
        # 3. Final Metadata object (ListingMetadata inherits from ItemExtraction)
        metadata = ListingMetadata(
            session_id=session_id,
            **extraction.model_dump()
        )
        
        # 4. Initialize the session in the database
        initial_state = NegotiationState(
            session_id=session_id,
            item_metadata=metadata,
            analytical_data=AnalyticalData(
                calculated_fair_market_avg=0.0,
                price_volatility=0.0,
                recommended_walk_away_price=0.0,
                is_researched=False
            ),
            history=[],
            current_lowball_price=0.0
        )
        await db.save_state(initial_state)
        
        # 5. Trigger the asynchronous Scraper task
        background_tasks.add_task(background_market_scrape, session_id, metadata.item_name, db)
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error.")
