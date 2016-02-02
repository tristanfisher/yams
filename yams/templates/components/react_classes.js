// React classes we need for component modeling
// yams_data is available at the time of the class instantiation


console.debug = console.debug || console.info;

function is_primitive_leaf(node){
    if (node instanceof Object){
        return false;
    }
    return true;
}

// build up our accessor
/*
There are two obvious ways to go about searching the tree for the subtree.

#1: Walk the depth of the subtree.  Use this path while walking the tree.
    When the subtree element isn't in the tree, return.

#2: Walk both trees simultaneously, return when at the end of the subtree or when we fail to match.
    The second has the benefit of stopping exactly in the subtree when needed on shallow depths
    (which might be useful if/when we get used to paint the DOM for X,000 elements ;)).

We could also optimistically just try to descend.
 */
function descend_tree(tree, search_subtree) {
    // tree - the tree to search
    // search_subtree - the potential subtree to retrieve
    // returns an array with the pruned down tree and a bool to denote whether or not the subtree was a complete subset
    // e.g. [pruned_tree, false]

    // todo: build this up to support more than a single depth subtree (e.g. for globbing on multiple keys)

    // if we're a primitive type, we'll end up with char indexes
    var search_subtree_keyname = Object.keys(search_subtree);

    //using `this` is barfing errors -- maybe a react thing?
    var result = result || "";
    //this.traversed_node_names = this.traversed_node_names || [];
    var traversed_node_names = traversed_node_names || [];
    var derived_external_node = "";

    if (yams_debug_mode){
        console.debug('tree status           => ' + tree + ' typeof: ' + typeof(tree) + ' keys: ' + Object.keys(tree));
        console.debug('search_subtree status => ' + search_subtree + ' typeof: ' + typeof(search_subtree) + ' keys: ' + search_subtree_keyname);
    }

    // e.g. if 'response' in next_node candidate keys. if not, we move to the value in the search subtree
    // todo: needs actual check of "if undefined" as [] or {} or false could erroneously default back to the full tree

    // if $tree is a string, skip, otherwise we'll TypeError
    //console.error(typeof(search_subtree) == 'object' || search_subtree instanceof Object);

    if (typeof(tree) == 'object' || tree instanceof Object) {

        if (search_subtree_keyname in tree) {

            //this.traversed_node_names.push(search_subtree_keyname);
            traversed_node_names.push(search_subtree_keyname);

            // move to that node in our tree and subtree for continued searching
            tree = tree[search_subtree_keyname];
            search_subtree = search_subtree[search_subtree_keyname];

            if (!(typeof search_subtree === "undefined")) {

                // on the tree, we have JSON.  the subtree won't be the same structure necessarily.
                // e.g. {headers: 'date' } vs {headers: {'date', 'etag'}}

                // probably a string or an int.
                if (is_primitive_leaf(search_subtree)) {

                    // not necessarily a leaf node, but we should have walked to the end of our subtree
                    derived_external_node = tree[search_subtree];

                    // todo: return an array like [status_of_success, data] ?
                    if (!(typeof derived_external_node === "undefined")) {
                        if (yams_debug_mode){
                            console.debug("Complete subtree matched.  Leaf => " + derived_external_node + " ;; Last matched node keys => " + Object.keys(tree));
                        }
                        //this.result = derived_external_node;
                        var result = derived_external_node;
                        return [derived_external_node, true];
                    } else {
                        if (yams_debug_mode) {
                            console.debug("Complete subtree did not match.  Leaf => " + derived_external_node + " ;; Last matched node keys => " + Object.keys(tree));
                        }
                        // this tree object has been pruned
                        return [tree, false];
                    }
                }
                else {
                    if (yams_debug_mode) {
                        console.debug("recursing");
                    }
                    descend_tree(tree, search_subtree);
                }
            }
            else {
                console.error("Search_subtree was undefined.  This is an error.  " +
                    "Please consider opening an issue on the project tracker with details: " + issue_project_tracker)
            }
        }
        else {
            // if we're here, we didn't match on the first key
            if (yams_debug_mode) {
                console.debug("Subtree did not match any of the API response tree.");
            }
            return [tree, false];
        }
    } else {
        // probably a string
        //if (typeof(tree) == 'string' || child instanceof String){
        console.info("Did not receive an object to search, returning the original object passed as a tree.");
        result = tree;
    }
    //return this.result;
    // typeof(tree) wasn't an object, which means we didn't process it
    return [result, false];
}

function percentage_to_bootstrap(size){
    // todo: make it do a thing
    return 6
}

function get_status_icon(status){
    if (status == 'ok'){
        var status_icon = "glyphicon glyphicon-ok";
    }
    else if (status == "warning"){
        var status_icon = "glyphicon glyphicon-question-sign";
    }
    else if (status == "disabled"){
        var status_icon = "glyphicon glyphicon-off";
    }
    else {
        var status_icon = "glyphicon glyphicon-fire";
    }
    return status_icon;
}

var SubtreeParseInlet = React.createClass({
    render: function(){
        // receives data and complete_subset
        var subtree = this.props.data;
        var subtree_was_complete_subset = this.props.complete_subset;
        var subtree_string = ""

        //for first pass through subtree_was_complete_subset will be undefined
        var subtree_defined = (typeof subtree_was_complete_subset !== "undefined");

        //// todo: work this into the UI, potentially on keyup when not total subtree
        if (subtree_defined){
            if (!(subtree_was_complete_subset)) {
                if (yams_debug_mode){
                    console.debug("Did not totally descend tree => " + subtree);
                }
                var subtree_notice = <div className="yamsSubtreeMatchText">The response did not meet our our expected path.  Last matching node:</div>;
                var subtree_json = JSON.stringify(subtree, null, 2);
                var subtree_string = <pre className="yamsSubtreeMatchText">{subtree_json}</pre>
            }
        }
        //could put the output here anyway -- could be cool to be able to expand to show the JSON that formed the display
        //else {
        //    subtree_string = JSON.stringify(subtree, null, 2);
        //
        //}

        return(
            <div className="yamsSubtreeMatchBox">
                {subtree_notice}
                {subtree_string}
            </div>
        )
    }
});

var Box = React.createClass({

    // TODO: work in the if display_type

    // aws:
    // "field": {"response": {"response": "status"}},
    // "field_type": "glob_string",
    // "display_type": "list"

    // github:
    //"logic": "boolean",
    //"field": {"response":"status"},
    //"field_type": "string",
    //"display_type": "list"

    // use getInitialState instead of || in the render
    getInitialState: function(){
        if (! this.props.enabled){
            var detail = 'This YAMS box is not enabled.';
            var status = 'disabled'
        }

        return {
            status: status || '',
            detail: detail || '[loading]',
            last_updated: '[never]'
        };
    },

    updateBoxData: function(){

        var pruned_tree = undefined;
        var tree_response = undefined;
        var subtree_was_complete_subset = undefined;
        var parser_message = "";
        var search_field_as_json = undefined;

        $.ajax({
            url: this.props.data.endpoint,
            dataType: 'json',
            cache: false,
            success: function(data) {
                try {

                    // todo: incorporate the above data logic for which field to search
                    // todo: if we have a successful search, no longer walk the JSON response.  if we don't,
                    //   display an interactive box that denotes "here's as far as i got" and maybe search on key-up?
                    // e.g. store the full-accessed-tree search on the box and use that direct accessor.

                    var search_field = this.props.data.field;
                    var pruned_tree = descend_tree(data, search_field);

                    var tree_response = pruned_tree[0];

                    // when we allow for customizable ok/warn/err string matches,
                    // this is a suitable place for the comparison
                    var tree_response_text = pruned_tree[0];
                    var subtree_was_complete_subset = pruned_tree[1];  // true or false

                    if (! subtree_was_complete_subset){
                        var search_field_as_json = JSON.stringify(search_field);
                        tree_response_text = "warning";
                        parser_message = "Could not locate specified field: " + search_field_as_json +
                                ".  The last matched node has been included."
                    } else {
                        // clear this out so we don't waste this effort
                        pruned_tree = undefined;
                    }

                    // todo: this needs to be relaxed for dealing with informational or non-yams plugins.
                    // re-use/extend descend_tree() if necessary
                    //var detail_field = descend_tree(data, this.props.detail_text_field);
                    var detail_field = data['response']['response'];

                    this.setState({
                        status: tree_response_text,
                        detail: detail_field,
                        parser_message: parser_message,
                        pruned_tree: tree_response,
                        subtree_was_complete_subset: subtree_was_complete_subset,
                        last_updated: new Date().toUTCString()
                    })
                }
                catch (err) {
                    console.error("Caught error trying to handle: " + this.props.data.endpoint
                        + ".  Error text: " + err.toString()
                    );

                    // return the pruned_tree if we can with our error.
                    this.setState({
                        status: "unknown",
                        detail: "[error] see console.",
                        parser_message: parser_message,
                        pruned_tree: pruned_tree,
                        subtree_was_complete_subset: subtree_was_complete_subset
                    })
                }
            }.bind(this),
            error: function(xhr, status, err){
                // if (xhr.status==404){...}
                console.error(this.props.data.endpoint, status, err.toString());
            }.bind(this)
        }); //.ajax

        // use settimeout instead of interval so we don't stack up requests in case
        // the remote server requires more than $interval to respond.
        var update_ms = this.props.data.update_method.interval_seconds * 1000;
        setTimeout(this.updateBoxData, update_ms)
    },

    componentDidMount: function(){

        $.get(this.props.data.endpoint, function(result){
            if(this.isMounted()){
                // todo: refresh this.props check periodically and/or via an enable/disable button
                if(this.props.enabled) {
                    this.updateBoxData();
                }
            }
        }.bind(this));
    },

    render: function(){

        // initial size needs to come from the server side.
        // use percentage_to_bootstrap(this.props.width) on updates to the DOM

        var _status = this.state.status || "warning";
        var subtree = this.state.pruned_tree;
        var subtree_was_complete_subset = this.state.subtree_was_complete_subset;

        // TODO: convert these to React components/classes
        return(
            <div className={"yamsBox col-xs-6"}>
                <div className="yamsBoxLabel">{this.props.label}</div>

                <div className="div-inline-first-children">
                    <div className="yamsBoxStatusTitle">Status: </div>
                    <div className={get_status_icon(_status) + " bg-" + _status}></div>
                </div>

                <div className="div-inline-first-children">
                    <div className="yamsBoxDetailTitle">Detail: </div>
                    <div className="">{this.state.detail}</div>
                </div>

                <SubtreeParseInlet data={subtree} complete_subset={subtree_was_complete_subset} />

                <div className="yamsBoxLastUpdated text-muted">
                    Last updated: {this.state.last_updated}
                </div>

            </div>
        );
    }
});

var BoxGroup = React.createClass({

    render: function(){
        var boxNodes = this.props.data.map(function(data) {
           return (
               <Box label={data.label} width={data.width} height={data.height} data={data.data} key={data.id} enabled={data.enabled} />
           )
        });

        return(
            <div className="yamsBoxGroup">
                {boxNodes}
            </div>
        );
    }
});


var Panel = React.createClass({
    render: function(){
        return(
            <div className="yamsPanel row">
                <div className="yamsPanelLabel">
                    <div className="yamsPanelLabelText">{this.props.label}</div>
                </div>
                <BoxGroup data={this.props.boxes} key={this.props.id} />
                {this.props.children}
            </div>
        );
    }
});

var PanelGroup = React.createClass({
    render: function(){
        var panelNodes = this.props.data.map(function(panel) {
           return (
               <Panel label={panel.label} key={panel.id} boxes={panel.boxes} />
           )
        });

        return(
            <div className="yamsGroup">
                {panelNodes}
            </div>
        )
    }
});

var ErrorPanel = React.createClass({
    render: function(){
        return(
            <div className="yamsGroup text-center">
                <h2>no data received to render</h2>
            </div>
        )
    }
});

if (typeof(yams_data !== "undefined")) {
    var panelgroup_to_render = <PanelGroup data={yams_data}/>;
} else {
    var panelgroup_to_render = <ErrorPanel data={yams_data}/>;
}

/*  List of panels, panels have lists of boxes
    [{panel[0] - box[0], box[1]}, {panel[1] - box[0], box[1], box[2]}]  */
ReactDOM.render(
    // poll for this data later to propagate changes down the model
    panelgroup_to_render,
    document.getElementById('container_panels')
);