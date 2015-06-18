(function main(){
    console.log('<< YAMS : github.com/tristanfisher/yams >>')
})()

function get_local(success_callback, f){

    var script = document.createElement('script');
    script.src = './static/' + f;

    var head = document.getElementsByTagName('head')[0];
    done = false;

    // attach handler
    script.onload = script.onreadystatechange = function(){
        if (!done && (!this.readyState || this.readyState == 'loaded' || this.readyState == 'complete')) {
            done = true;

            success_callback()

            script.onload = script.onreadystatechange = null;
            head.removeChild(script);
        }; //done/load check
    };//script.onload
    head.appendChild(script);
    console.log("Loading cached: " + f)
}; //get_local()

function main(){
}

// could use this as a try/catch handler
// check_def(React, 'react-0.13.3.min.js')
function check_def(s, f){
    if (typeof s == 'undefined'){
        get_local(main, f)
    }
}

// Might need a setTimeout to give objects time to load.
//https://facebook.github.io/react/downloads.html
if (typeof React == 'undefined'){
    get_local(main, 'js/plugins/react/react.min.js')
};