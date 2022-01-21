//
// 画面共通のjavascript
//

// http getリクエスト
function urlGet(url, params = {}, cbfunc = (data) => {})
{
  let query = '';

  if (Object.keys(params).length) {
    const query_params = new URLSearchParams(params); 
    query = '?' + query_params;
  }

  fetch(url + query, {
    method: 'GET'
  }).then((response) => {
    if(!response.ok) {
      // エラーレスポンス
      message = "response code: " + response.status;
      console.log(message);
    } 
    return response.json();
  }).then((data) => {
    cbfunc(data);
  }).catch((error) => {
    // エラー
    console.log(error);
  });
}

// http postリクエスト
function urlPost(url, data, cbfunc)
{
  fetch(url, {
    method: 'POST', body: data
  }).then((response) => {
    if(!response.ok) {
      // エラーレスポンス
      message = "response code: "+ response.status;
      console.log(message);
    } 
    return response.json();
  }).then((data) => {
    cbfunc(data);
    console.log(data);
  }).catch((error) => {
    // 通信エラー
    console.log(error);
  });
}

