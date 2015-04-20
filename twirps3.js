;(function(){

    var width = 960, 
        height =680;

    var color = d3.scale.category20();

    var force = d3.layout.force()
        .charge(-700)
        .friction(0.4)
        .size([width, height]);

    var svg; 
    var displayedNodes = [],
        displayedEdges = [];



    //mapData = JSON.parse('map.json')
    //console.log(JSON.stringify(mapData, null, 2))
    d3.json('map_d3_improved.json', function(error, map){
        
        displayedNodes = map.nodes.slice(3,4);
        
        var displayedHandles = {};

        displayedNodes.forEach(function(d){
            displayedHandles[d.handle] = displayedNodes.indexOf(d);
        });
        


        
        redraw();

        var link;
        var node;

        d3.select('body').on('dblclick', function(){
            addManyNodes});

        function addManyNodes(){
            d3.select('.node').forEach(addNode)
        }

        function redraw(){
            
            d3.selectAll('svg').remove();

            svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);

            force
                .nodes(displayedNodes)
                .links(displayedEdges)
                .linkDistance(Math.sqrt(100000/displayedNodes.length))
                .start();

            link = svg.selectAll(".link")
                .data(displayedEdges)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width",  function(d){return Math.ceil(Math.log(d.value))});

            node = svg.selectAll(".node")
                .data(displayedNodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", function(d){return Math.log(d.tweets*50/displayedNodes.length)})
                .call(force.drag)
                .attr("clicked", 0)
                .style("fill", function(d) { return color(d.party); })
                .attr("party", function(d){return d.party})
                .attr("id", function(d){return d.handle})
                //.on("dblclick", addNode)

                



            force.links().forEach(function(d){
                d3.select('#'+d.source.handle).attr("clicked", 1)
            });            

            node.append("title")
                .text(function(d){return d.name;})
        };

        function addNode(clickedNode){
            // console.log(force.nodes())
            // console.log(displayedNodes)              
            
        
            var cNode = d3.select(clickedNode).node()

            var contact = ['mentions', 'retweets']

            for (var i=0; i<contact.length; i++){
                displayedNodes.forEach(function(d){displayedHandles[d.handle]=displayedNodes.indexOf(d);});
                for (twirpContact in cNode[contact[i]]){
                    if (displayedHandles[twirpContact]== undefined){
                        //console.log(displayedHandles)
                        //console.log(twirpContact)

                        for (j=0;j<map.nodes.length; j++){

                            if (map.nodes[j].handle == twirpContact &&
                                cNode[contact[i]][twirpContact]>10){

                                displayedNodes.push(map.nodes[j]);
                            };
                        };  
                    };
                };
            };
            //displayedNodes.forEach(function(d){console.log(d.handle);});   
            click  = d3.select(this)
            if (click.attr("clicked") == 0){
                force.stop();
                calculateEdges(clickedNode);
                redraw();
                d3.select('#'+cNode.handle).attr("clicked", 2);
            };
        };


        function calculateEdges(clickedNode){
            displayedNodes.forEach(function(d){displayedHandles[d.handle]=displayedNodes.indexOf(d);});
            console.log(displayedHandles)
            

            var cNode = d3.select(clickedNode).node()

            var contact = ['mentions', 'retweets']
   
            for (i=0; i<contact.length; i++){
                
                for(var mentionHandle in cNode[contact[i]]){
                    
                    if (mentionHandle in displayedHandles){

                        var newEdge = {source: displayedHandles[cNode.handle],
                                   target: displayedHandles[mentionHandle], 
                                   value: cNode[contact[i]][mentionHandle],
                                   contact: contact[i]
                                };

                        if (newEdge.value > 10){
                            displayedEdges.push(newEdge);

                        };       
                    };
                
                };
            };
            //console.log(displayedEdges)
            //});
            console.log(displayedEdges);
            displayedNodes.forEach(function(d){console.log(d.name)});
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