const path = require('path');
const fs = require('fs');

/**
 * A plain JavaScript script to verify our Mobile API Service Layer.
 * This avoids TS-node environment issues while still testing the 
 * exact endpoints and headers used by the mobile app.
 */
async function runTest() {
  console.log("--- STARTING MOBILE API VERIFICATION (JS) ---");
  
  const API_BASE_URL = 'http://127.0.0.1:8000';
  const API_V1_STR = '/api/v1';
  const API_TOKEN = 'lowball_debug_token';
  
  const testImagePath = path.join(__dirname, '..', '..', 'backend', 'tests', 'general_image_test.png');
  
  try {
    console.log(`Step 1: Uploading image to Vision Agent... (${testImagePath})`);
    
    // Simulate the FormData payload manually for Node
    const FormData = require('form-data');
    const form = new FormData();
    form.append('file', fs.createReadStream(testImagePath));

    const axios = require('axios');
    const response = await axios.post(`${API_BASE_URL}${API_V1_STR}/listing/analyze`, form, {
      headers: {
        ...form.getHeaders(),
        'X-API-Token': API_TOKEN,
      },
    });
    
    console.log("\n✅ API RESPONSE SUCCESSFUL:");
    console.log(JSON.stringify(response.data, null, 2));
    
    console.log("\n--- VERIFICATION COMPLETE ---");
  } catch (err) {
    console.error("\n❌ API VERIFICATION FAILED:");
    if (err.response) {
      console.error(`Status: ${err.response.status}`);
      console.error(err.response.data);
    } else {
      console.error(err.message);
    }
    process.exit(1);
  }
}

runTest();
