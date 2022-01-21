//
// ��ʋ��ʂ�javascript
//

// http get���N�G�X�g
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
      // �G���[���X�|���X
      message = "response code: " + response.status;
      console.log(message);
    } 
    return response.json();
  }).then((data) => {
    cbfunc(data);
  }).catch((error) => {
    // �G���[
    console.log(error);
  });
}

// http post���N�G�X�g
function urlPost(url, data, cbfunc)
{
  fetch(url, {
    method: 'POST', body: data
  }).then((response) => {
    if(!response.ok) {
      // �G���[���X�|���X
      message = "response code: "+ response.status;
      console.log(message);
    } 
    return response.json();
  }).then((data) => {
    cbfunc(data);
    console.log(data);
  }).catch((error) => {
    // �ʐM�G���[
    console.log(error);
  });
}

