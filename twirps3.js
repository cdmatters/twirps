;(function(){

    var width = 960, 
        height =400;

    var color = d3.scale.category20()

    var force = d3.layout.force()
        .charge(-500)
        .linkDistance(30)
        .friction(0.2)
        .size([width, height]);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    var displayedNodes = [],
        displayedEdges = [];

    //mapData = JSON.parse('map.json')
    //console.log(JSON.stringify(mapData, null, 2))
    d3.json('map_d3.json', function(error, map){
        
        displayedNodes= map.nodes.slice(1,2);
        var displayedHandles = {};
        displayedNodes.forEach(function(d){displayedHandles[d.handle]=displayedNodes.indexOf(d);});
        


        
        redraw();
        console.log(force.nodes())

         var link;
         var node;

        function redraw(){
            d3.selectAll('svg').remove();

            svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);

            force
                .nodes(displayedNodes)
                .links(displayedEdges)
                .start();

            link = svg.selectAll(".link")
                .data(displayedEdges)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width",   1);

            node = svg.selectAll(".node")
                .data(displayedNodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 5)
                .style("fill", function(d){return color(d.party_no);})
                .call(force.drag)
                .on("dblclick", addNode)

                node.append("title")
                .text(function(d){return d.name;});
        };

        function addNode(clickedNode){
            console.log(force.nodes())
            console.log(displayedNodes)  
        
            // var newvar = force.nodes()
            // displayedNodes = newvar.slice(0)

            //  var newvar = force.nodes()
            //  var newvar2 = newvar.slice()
            //  console.log(newvar);
            //  console.log(newvar2);
            //  console.log(displayedNodes)   

            

            var clickedNode = d3.select(clickedNode).node()
            for (mentioned in map.old[clickedNode.handle].mentions){
                if (displayedHandles[mentioned]== undefined){
                    //console.log(mentioned)
                    //console.log(Object.keys(displayedHandles))

                    for (i=0;i<map.nodes.length; i++){

                        if (map.nodes[i].handle == mentioned){
                            displayedNodes.push(map.nodes[i]);
                        };
                    };  
                };
            }
            //displayedNodes.forEach(function(d){console.log(d.handle);});   
            force.stop;
            calculateEdges(clickedNode);

            redraw();
        };


        function calculateEdges(clickedNode){
            displayedHandles = {}

            displayedNodes.forEach(function(d){displayedHandles[d.handle]=displayedNodes.indexOf(d);});
            ////console.log(displayedHandles)
            //displayedNodes.forEach(function(d){

            var clickedNode = d3.select(clickedNode).node()

            for(var mentionHandle in map.old[clickedNode.handle].mentions){
                
                if (mentionHandle in displayedHandles){

                    var newEdge = {source: displayedHandles[clickedNode.handle],
                               target: displayedHandles[mentionHandle], 
                               value: map.old[clickedNode.handle].mentions[mentionHandle],
                               contact:'mentions'
                            };
                    //console.log(newEdge)
                    if (newEdge.value > 5){
                        displayedEdges.push(newEdge);     
                    }       
                };
            
            };
            //console.log(displayedEdges)
            //});

            };






        force.on("tick", function(){
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr('cx', function(d) {return d.x;})
                .attr('cy', function(d) {return d.y;});
        })
    });



})();