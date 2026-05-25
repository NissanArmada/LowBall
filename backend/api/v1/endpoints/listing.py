from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from models.schemas import ListingMetadata, NegotiationState, AnalyticalData
from services import vision, scraper, store
from core.config import settings
from core.dependencies import get_store
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

async def background_market_scrape(session_id: str, item_name: str, db: store.SessionStore):
    """
    Background task to perform market scraping and update the session's analytical data.
    """
    try:
        # 1. Perform the real market analysis
        analytical_res = await scraper.scraper.analyze_market(item_name)
        
        # 2. Load current state
        state = await db.load_state(session_id)
        if state:
            # 3. Update with real data
            state.analytical_data = analytical_res
            await db.save_state(state)
            logger.info(f"Updated analytical data for session {session_id} after background scrape.")
        else:
            logger.warning(f"Could not find session {session_id} to update analytical data.")
            
    except Exception as e:
        logger.error(f"Background scrape failed for session {session_id}: {str(e)}")

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
        # We need to handle the fact that vision.analyze_image might not set session_id
        temp_metadata = await vision.analyze_image(image_content)
        
        # 2. Generate permanent session_id
        session_id = str(uuid.uuid4())
        
        # 3. Final Metadata object
        metadata = ListingMetadata(
            session_id=session_id,
            item_name=temp_metadata.item_name,
            original_listing_price=temp_metadata.original_listing_price,
            suggested_low_price=temp_metadata.suggested_low_price,
            suggested_high_price=temp_metadata.suggested_high_price,
            condition=temp_metadata.condition,
            description=temp_metadata.description
        )
        
        # 4. Initialize the session in the database
        initial_state = NegotiationState(
            session_id=session_id,
            item_metadata=metadata,
            analytical_data=AnalyticalData(
                calculated_fair_market_avg=0.0,
                price_volatility=0.0,
                recommended_walk_away_price=0.0
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
