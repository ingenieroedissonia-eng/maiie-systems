content = open('maiie-web/src/services/apiService.js', 'r', encoding='utf-8').read()

addition = '''
export const getSubmissions = async (missionId) => {
  try {
    const response = await fetch('/api/submissions?id=' + missionId, {
      headers: { 'x-app-token': APP_TOKEN },
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error' }));
      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed.');
  }
};'''

open('maiie-web/src/services/apiService.js', 'w', encoding='utf-8').write(content + addition)
print('OK')
