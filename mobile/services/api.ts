import { Platform } from 'react-native';
import { Config } from '../constants/Config';
import { ListingMetadata } from '../constants/Types';

/**
 * Service for interacting with the Lowball.ai REST API
 */
export const ApiService = {
  /**
   * Uploads a screenshot to the backend for vision analysis.
   */
  async analyzeListing(imageUri: string): Promise<ListingMetadata> {
    const formData = new FormData();
    
    const filename = imageUri.split('/').pop() || 'upload.png';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : `image/png`;

    // To ensure compatibility with FastAPI and Gemini's strict byte parsing,
    // we fetch the URI and convert it to a true Blob across all platforms.
    try {
      const response = await fetch(imageUri);
      const blob = await response.blob();
      formData.append('file', blob, filename);
    } catch (e) {
      console.warn("Blob conversion failed, falling back to Native object format", e);
      // Fallback for older Native environments
      // @ts-ignore
      formData.append('file', {
        uri: imageUri,
        name: filename,
        type,
      });
    }

    const response = await fetch(`${Config.API_BASE_URL}${Config.API_V1_STR}/listing/analyze`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        'X-API-Token': Config.API_TOKEN,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `Analysis failed with status ${response.status}`);
    }

    return response.json();
  },
};
