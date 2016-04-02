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

    var clickedNodes=[];
    var lastClickedNode;

    var toggle = {
        radius:false,
        highlight:false,
        pop_all:false
    };


    function requestMapToD3Map(backend_map){
        return { visibleNodes:backend_map.nodes,
                 visibleEdges:[]                }
    }

    function generateMap(error, server_map){
        var map = requestMapToD3Map(server_map);

        visibleNodes = map.visibleNodes.slice();
        visibleEdges = map.visibleEdges.slice();

        allNodes = map.visibleNodes.slice();
        allEdges = map.visibleEdges.slice();

        force = d3.layout.force()
            .charge(-200)
            .gravity(.5)
            .linkDistance(10)
            .linkStrength(2)
            .chargeDistance(10000)
            .size([width, height])
            .start();

        redrawMap();

        force.on("tick", function(){
            moveItems();
        });

    }

    function redrawMap(){
        d3.selectAll('svg').remove();
        drawMap();
    }

    function drawMap(){
        svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);
      
        force
            .nodes(allNodes)
            .links(allEdges)
            .start()

        // draw nodes
        node = svg.selectAll(".node")
             .data(allNodes)
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
        node.append("title")
             .text(function(d){return d.name})

        // draw links
        link = svg.selectAll(".link")
              .data(allEdges)
             .enter().append("path")
              .attr("class", "link")
              .style("stroke-width", 1)
              .style("stroke-opacity", 0.5)
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

        // draw customiseable features
        node.selectAll("circle")
             .attr("r", function(d){return (d.clicked==1 && toggle.radius==true)?5+Math.sqrt(d.tweets/100):5;})
             .style("stroke-opacity", function(d){return (d.clicked==0)?0.5:1;})
             .style("stroke-width", function(d){return (d.clicked==0)?3:1.5;})
        node.selectAll("text")
             .text(function(d){return (d.clicked==1 && toggle.radius==true)?d.name:undefined;})
    
        //highlightTransition();
    } 

    function clickNode(){

    }


    function moveItems(){
        
        function border(z, axis ){
            var r = 5; 
            if (axis == 'x'){return Math.max(2*r, Math.min(width-2*r, z))}
            else if (axis == 'y'){return Math.max(2*r, Math.min(height-2*r, z))};
        }

        function linkBezierPath(data){
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

    

    d3.json(map_url, generateMap);

})();