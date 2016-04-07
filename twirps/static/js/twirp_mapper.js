;(function() {
    
    var map_url = $SCRIPT_ROOT+'/data'+$INITIAL_LOAD;
    console.log(map_url);

    var width = 2000,
        height = 1200;

    var parties_map = {
        "Conservative":"#0575c9",
        "Labour":"#ed1e0e",
        "Liberal Democrat":"#fe8300",
        "UKIP":"#712f87",
        "Green":"#78c31e",
        "Scottish National Party":"#EBC31C",
        "Social Democratic and Labour Party":"#65a966",
        "DUP":"#c0153d",
        "Sinn Fein":"#00623f",
        "Alliance":"#e1c21e",
        "Respect":"#31b56a",
        "Plaid Cymru":"#4e9f2f",
        "Independent":"#4e9f2f",
        "UUP":"#4e9f2f"
    }

    var force,
        node,
        link,
        mark;

    var svg;

    var visibleNodes = [],
        visibleEdges = [],
        invisibleNodes = [],
        invisibleEdges= [],
        allNodes = [],
        allEdges = [];

    // used to generate links based on handles
    // not place in node array.
    var visibleNodesHandleMap = {};

    var lastClickedNode;
    var lastClickedNodeNeighbours = [];

    var toggle = {
        radius:false,
        highlight:false,
        click_all:false,
        cycle_focus:false,
        cycle_count:0,
        _start_BFS:false // non permanent
    };


    function keyController(){
        var key = d3.event.keyCode;
        console.log(key)

        if  (key == 119 || key == 87 ) // (w|W)
        {
            toggle.radius = (!toggle.radius);
            radiusTransition();
        } 
        else if (key == 115 || key == 83) // (s|S)
        {
            toggle.highlight = (!toggle.highlight);
            highlightTransition();
        }
        else if (key == 120 || key == 88) // (x|X)
        {
            toggle.click_all = (!toggle.click_all);
            clickAllTransition();
        } 
        else if (key == 106 || key == 74) // (j|J)
        {
            toggle.cycle_focus = true;
            cycleFocusTransition(1);
        }
        else if (key == 108 || key == 76) // (l|L)
        {
            toggle.cycle_focus = true;
            cycleFocusTransition(-1);
        }
        else if (key == 107 || key == 75) // (k|K)
        {
            toggle.cycle_focus = false;
            cycleFocusTransition(0);
        }
        else if (key == 105 || key == 73) // (i|I)
        {
            clickFocusTransition();
        }
        else if (key == 98 || key == 66) // (b|B) - non permanent
        {
            toggle._start_BFS = (!toggle._start_BFS);
            _crawlerBFS();
        }
        else if (key == 111 || key == 79) // (o|O) - non permanent
        {
            toggle._start_BFS = (!toggle._start_BFS);
            _crawlerBFS(tombstone=true); // one layer
        }

    }

    function requestMapToD3Map(backend_map){
        function filterTweetType(nodeList, passes){
            return nodeList.forEach( function(node, index, array){
                for (relationshipType in node.relationships){
                    if (relationshipType != passes){
                        delete node.relationships[relationshipType]
                    }
                }
                array[index]=node
            })
        }
        filterTweetType(backend_map.nodes, 'no_by_proxy');

        return { 
            visibleNodes:backend_map.nodes,
            visibleEdges:[]
        }
    }

    function generateMap(error, server_map){
        var map = requestMapToD3Map(server_map);

        visibleNodes = map.visibleNodes.slice();
        visibleEdges = map.visibleEdges.slice();

        allNodes = map.visibleNodes.slice();
        allEdges = map.visibleEdges.slice();

        visibleNodes.forEach(function(d){ 
            visibleNodesHandleMap[d.handle] = visibleNodes.indexOf(d)
        });

        force = d3.layout.force()
            .charge(-200)
            .gravity(.5)
            .linkDistance(Math.sqrt(150000/visibleNodes.length))
            .linkStrength(2)
            .chargeDistance(10000)
            .size([width, height])
            .start();

        redrawMap();

        d3.select("body").on("keypress", keyController)

        force.on("tick", function(){
            moveItems();
        });

    }

    function redrawMap(){
        d3.selectAll('svg').remove();
        svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);
      
        drawMap();
    }

    function drawMap(){

        force
            .nodes(allNodes)
            .links(allEdges)
            .start()
        
        // draw order: links under arrows under nodes

        // draw links
        link = svg.selectAll(".link")
              .data(visibleEdges)
             .enter().append("path")
              .attr("class", "link")
              .style("stroke-width", 1)
              .style("stroke-opacity", 0.5)
              .style("fill", "none")
              .style("stroke", function(d){return (d.contact=='mentions')?'grey':'black'})
              .style("marker-end", "url(#end)")
        
        // draw arrowheads
        mark = svg.append("defs").selectAll("marker")
              .data( visibleEdges.map(function(d){return d.source.handle}))
             .enter().append("marker")
              .attr("id", "end")
              .attr("viewBox", "0 -5 10 10")
              .attr("refX", 20)
              .attr("refY", -5)
              .attr("markerWidth", 6)
              .attr("markerHeight", 6)
              .attr("orient", "auto")
             .append("path")
              .attr("d", "M0,-5L10,0L0,5 L10,0 L0, -5")
              .attr("class", function(d){return d}) // the link's source's handle
              .style("stroke", function(d){ return (d.contact=='mentions')?'grey':'black'})
              .style("stroke-opacity", 0.5)

        // draw nodes
        node = svg.selectAll(".node")
             .data(visibleNodes)
           .enter().append("g")
             .attr("class", "node")
             .attr("id", function(d){return d.handle})
             .call(force.drag)
        node.append("circle")
             .attr("clicked", function(d){return d.clicked})
             .attr("fill", function(d){ return parties_map[d.party]})
             .attr("party", function(d){return d.party})
             .style("stroke", "white")
             .on("click", clickNode)
        node.append("text")
             .text(function(d){return })
             .attr("dx", -25)
             .attr("dy", 5)
             .style("stroke", "black")
             .on("click", clickNode)
        node.append("title")
             .text(function(d){return d.name})

        // draw customiseable features
        node.selectAll("circle")
             .style("stroke-opacity", function(d){return (d.clicked==0)?0.5:1;})
             .style("stroke-width", function(d){return (d.clicked==0)?3:1.5;})
             .attr("r", function(d){return (d.clicked==1 && toggle.radius==true)?5+Math.sqrt(d.tweets/100):5;})
        node.selectAll("text")
             .text(function(d){return (d.clicked==1 && toggle.radius==true)?d.name:undefined;})
    
    } 

    function getLinkedNodes(clickedNode){
        handleArray = []
        visibleEdges.forEach(function(d){
            if (d.source.handle==clickedNode.handle){
                handleArray.push(d.target.handle)
                }
        });

        return handleArray; 
    }

    function clickNode(clickedNode){

        if (clickedNode.clicked==0){
            clickedNode.clicked=1;
            addNodesBezierEdges(clickedNode);
            redrawMap();
        }

        clearFocusTransition(); // clear the black ring
        
        lastClickedNode = clickedNode;
        lastClickedNodeNeighbours = getLinkedNodes(clickedNode);
        
        highlightTransition();   // apply the highlight
        cycleFocusTransition(0)  // apply the black ring, but dont cycle it

    }

    function addNodesBezierEdges(clickedNode){

        for (contactType in clickedNode.relationships){
            var contacts = clickedNode.relationships[contactType]

            for ( targetHandle in contacts){
                
                //  ERROR: if node not plotted, ignore & continue
                if  (visibleNodesHandleMap[targetHandle] == undefined){
                    console.log("Missing node: "+targetHandle+" for "+clickedNode.handle);
                    continue;
                }
                
                var s_index = visibleNodesHandleMap[clickedNode.handle], 
                    t_index = visibleNodesHandleMap[targetHandle];

                var s = visibleNodes[s_index],
                    t = visibleNodes[t_index],
                    i = {};

                var invisibleEdgeA = {source : s, target : i},
                    invisibleEdgeB = {source : i, target : t};

                var visibleEdge = {
                        source:s, inter:i, target:t,
                        contactType:contactType, value:contacts[targetHandle][0], url:contacts[targetHandle][1] 
                }
                
                console.log(targetHandle +': '+visibleEdge.url)

                if (s.handle != t.handle){
                    invisibleNodes.push(i);
                    invisibleEdges.push(invisibleEdgeA, invisibleEdgeB);

                    visibleEdges.push(visibleEdge);

                    allNodes.push(i)
                    allEdges.push(invisibleEdgeA, invisibleEdgeB, visibleEdge)

                    // node.push(i)
                    // link.push(visibleEdge)
                }
            
            }

        }
    }

    function moveItems(){

        function border(z, axis ){
            var r = 5; 
            if (axis == 'x'){return Math.max(2*r, Math.min(width-2*r, z))}
            else if (axis == 'y'){return Math.max(2*r, Math.min(height-2*r, z))};
        }

        function linkBezierPath(d){
            return  "M" + border(d.source.x,'x') + "," + border(d.source.y,'y')
                  + "S" + border(d.inter.x, 'x') + "," + border(d.inter.y, 'y')
                  + " " + border(d.target.x,'x') + "," + border(d.target.y,'y');
        }

        function nodeTranslate(d){
            return "translate("+ border(d.x,'x') + ","
                               + border(d.y,'y') + ")";
        }

        link.attr("d", linkBezierPath);
        node.attr("transform", nodeTranslate);
    }


    // ---------------------------------------- //
    //               TRANSITIONS                //
    // ---------------------------------------- //


    function radiusTransition(){
        if (toggle.radius==true){
            node.selectAll('circle')
                  .transition()
                  .duration(2000)
                  .attr("r", function(d){return d.clicked==1?5+ Math.sqrt(d.tweets/100):5;});
            node.selectAll('text')
                  .text(function(d){return d.clicked==1?d.name:''});
        
        } else if (toggle.radius ==false){
            node.selectAll('circle')
                  .transition()
                  .duration(2000)
                  .attr("r", function(d){return 5;});
            node.selectAll('text')
                  .text(function(d){return;})
        }
    }

    function highlightTransition(){
        if (lastClickedNode == undefined){
            // nothing to highlight
            return;
        }

        if (toggle.highlight==true){
            var highlightedNodes = getLinkedNodes(lastClickedNode)
            highlightedNodes.push(lastClickedNode.handle);

            node.selectAll("circle")
                  .transition()
                  .duration(1000)
                  .attr('opacity', function(d){
                      return (highlightedNodes.some(function(e){return d.handle==e;}))?1:0.1;
                  });
            node.selectAll("text")
                  .transition()
                  .duration(3000)
                  .text(function(d){
                      return (highlightedNodes.some(function(e){return d.handle==e;})&& toggle.radius==true)?d.name:undefined;
                  });
            
            link.style("stroke-opacity", function(d){return (d.source.handle==lastClickedNode.handle)?1:0.05});
            
            svg.selectAll("marker").selectAll("path")
                  .style("stroke-opacity",0.05)
        
        } else {
            node.selectAll("circle")
                  .transition()
                  .duration(1000)
                  .attr('opacity', 1);

            node.selectAll("text")
                  .text(function(d){return (toggle.radius == true && d.clicked==1)?d.name:undefined;});

            link.style('stroke-opacity', 0.5);

            svg.selectAll("marker").selectAll("path")
                  .style("stroke-opacity",0.5);
        }

    }

    function clickAllTransition(){
        if (toggle.click_all==true){

            var nodes = visibleNodes.slice();

            function clicker(initial, nodes){
                return function(){
                    if (initial<nodes.length){
                        clickNode(nodes[initial]);
                        initial+=1;
                    }
                }
            }

            clickNodeTimer = clicker(0, nodes);
            
            // click first node instantly
            clickNodeTimer();
            
            toggle.clicker = window.setInterval(clickNodeTimer,1500);
        
        } else {
            window.clearInterval(toggle.clicker);
        }
    }


    function cycleFocusTransition(increment){
        if (lastClickedNode==undefined){
            // ERROR: No nodes to cycle through
            return -1;
        } else if (lastClickedNodeNeighbours.length == 0){
            console.log("Error: node has no links, cant focus");
            return -1;
        }

        selectedHandle = lastClickedNodeNeighbours[toggle.cycle_count]

        d3.select('#'+selectedHandle).select('circle')
                //.transition()
                .style("stroke", "white")
                .style("stroke-opacity", function(d){return (d.clicked==0)?0.5:1;})
                .style("stroke-width", function(d){return (d.clicked==0)?3:1.5;})

        if (toggle.cycle_focus){

            toggle.cycle_count += increment;
            toggle.cycle_count = toggle.cycle_count % lastClickedNodeNeighbours.length 
            
            if (toggle.cycle_count<0){ 
                toggle.cycle_count += lastClickedNodeNeighbours.length
            }           

            selectedHandle = lastClickedNodeNeighbours[toggle.cycle_count];

            d3.select('#'+selectedHandle).select('circle')
               // .transition()
                .style("stroke", "black")
                .style("stroke-opacity", 1)
                .style("stroke-width", 1)
        }
        else
        {
            toggle.cycle_count = 0;
        }
    }

    function clearFocusTransition(){
        selectedHandle = lastClickedNodeNeighbours[toggle.cycle_count]

        d3.select('#'+selectedHandle).select('circle')
                .style("stroke", "white")
                .style("stroke-opacity", function(d){return (d.clicked==0)?0.5:1;})
                .style("stroke-width", function(d){return (d.clicked==0)?3:1.5;})
    }

    function clickFocusTransition(){
        if (toggle.cycle_focus){
            selectedHandle = lastClickedNodeNeighbours[toggle.cycle_count]

            n_index = visibleNodesHandleMap[selectedHandle]
            clickNode(visibleNodes[n_index])
        }
    }

    function _crawlerBFS(tombstone){
        if (toggle._start_BFS){            
            var queue = lastClickedNodeNeighbours.filter( 
                    function(d){return visibleNodes[visibleNodesHandleMap[d]].clicked==0}
            );
            if (tombstone==true){
                queue.push('STOP_BFS')
            }
            function _bfs(){
                return function(){
                        console.log('hey')
                        if (queue.length!=0 && queue[0]!='STOP_BFS'){
                            b_index = visibleNodesHandleMap[queue.shift()]
                            clickNode(visibleNodes[b_index]);

                            unclickedNeighbours = lastClickedNodeNeighbours.filter( 
                                function(d){return visibleNodes[visibleNodesHandleMap[d]].clicked==0}
                            );

                            queue = queue.concat(unclickedNeighbours);
                        } else {
                            // clean up after yourself
                            toggle._start_BFS=false;
                            window.clearInterval(toggle._BFS);
                        }
                    }
            }

            bfs_closure = _bfs();
            toggle._BFS = window.setInterval(bfs_closure, 1000)
        } else {
            window.clearInterval(toggle._BFS);
        }

    }


    d3.json(map_url, generateMap);



})();