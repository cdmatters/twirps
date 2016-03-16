;(function(){
    console.log("Testing this");
    
    function load_into_h1(data){
        $("p").prepend("<h1>"+data.msg+"</h1>");
    }


    $.getJSON($SCRIPT_ROOT + '/string',{}, load_into_h1)
})();