content = open('maiie-web/src/services/apiService.js', encoding='utf-8').read()

new_functions = """
export const getGraph = async (missionId) => {
  try {
    const response = await fetch(/api/mission//graph, {
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
};

export const getSubmissionDetail = async (missionId, subId) => {
  try {
    const response = await fetch(/api/mission//submission/, {
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
};
"""

open('maiie-web/src/services/apiService.js', 'w', encoding='utf-8').write(content + new_functions)
print('OK getGraph:', 'getGraph' in content + new_functions)
print('OK getSubmissionDetail:', 'getSubmissionDetail' in content + new_functions)
print('OK getSubmissions intacto:', 'getSubmissions' in content)
