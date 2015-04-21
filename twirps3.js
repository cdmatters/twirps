;(function(){

    var width = 2000, 
        height =800;

    var parties_map= {"Conservative":"#0575c9", "Labour":"#ed1e0e",
        "Liberal Democrat":"#fe8300", "UKIP":"#712f87", "Green":"#78c31e",
        "Scottish National Party":"#EBC31C", "Social Democratic and Labour Party":"#65a966",
        "DUP":"#c0153d", "Sinn Fein":"#00623f", "Alliance":"#e1c21e", "Respect":"#31b56a",
        "Plaid Cymru":"#4e9f2f", "Independent":"#4e9f2f", "UUP":"#4e9f2f"
         };

   // var color = d3.scale.category20()
                    //ordinal()
                  // .domain(Object.keys(parties_scale))
                  // .range(Object.keys(parties_scale).forEach(function(d){return parties_scale[d];}));

    


    var force = d3.layout.force()
        .charge(-200)
        .gravity(.5)
        .linkDistance(10)
        .linkStrength(2)
        .size([width, height]);

    var svg; 

    var displayedNodes = [],
        displayedEdges = [],
        displayedInvisibleEdges = [],
        displayedInvisibleNodes = [],
        poppedNodes=[];




    //mapData = JSON.parse('map.json')
    //console.log(JSON.stringify(mapData, null, 2))
    d3.json('map_d3_improved.json', function(error, map){
        
        displayedNodes = map.nodes.slice();
        displayedInvisibleNodes = displayedNodes.slice()
        
        
        var displayedHandles = {};
        var link;
        var node;



        
        updateDisplayedNodes();
        redraw();


        function updateDisplayedNodes(){
            
            displayedNodes.forEach(
                function(d){ displayedHandles[d.handle] = displayedNodes.indexOf(d)}
            );
        }


        function redraw(){
            
            d3.selectAll('svg').remove();

            svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);

            // console.log(displayedNodes.length);
            // console.log(displayedInvisibleNodes.length);
            
            // console.log(displayedEdges.length);
            // console.log(displayedInvisibleEdges.length);

            force
                .nodes(displayedInvisibleNodes)
                .links(displayedInvisibleEdges)
                .linkDistance(Math.sqrt(100000/displayedNodes.length))
                .start();



            link = svg.selectAll(".link")
                .data(displayedEdges)
              .enter().append("path")
                .attr("class", "link")
                .style("stroke-width",  1)
                .style("stroke", function(d){
                 // console.log(d[3])
                  if (d[3]=='mentions'){
                    //console.log('hey')
                    return 'grey';}
                  else {
                    return 'black';};
                   })
                .style("marker-end", "url(#end)")

            svg.append("defs").selectAll("marker")
                .data(["end"])
              .enter().append("marker")
                .attr("id", function(d){console.log(d);return d;})
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", -1.5)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
              .append("path")
                .attr("d", "M0,-5L10,0L0,5 L10,0 L0, -5")
                .style("stroke", function(d){
                 // console.log(d[3])
                  if (d[3]=='mentions'){
                    //console.log('hey')
                    return 'grey';}
                  else {
                    return 'black';};
                   })
                .style("stroke-opacity",0.5);


            node = svg.selectAll(".node")
                .data(displayedNodes)
              .enter().append("circle")
                .attr("class", "node")
                .attr("r", function(d){return 5})// + (d.tweets/5000)})
                .call(force.drag)
                .attr("clicked", 0)
                .attr("fill", function(d) {return parties_map[d.party]; })
                .style("stroke", 'white' )
               // .style("stroke-width", 7)
                .style("stroke-opacity",0.5)
                .attr("party", function(d){return d.party})
                .attr("id", function(d){return d.handle})
                .on("click", addNode)
                .on("mouseover", null);




                
            force.links().forEach(function(d){
                d3.select('#'+d.source.handle).attr("clicked", 1)
            });            

            node.append("title")
                .text(function(d){return d.name;});

            node.style("stroke-opacity", function(d){
                var clicked = d3.select('#'+d.handle).attr("clicked")
               // console.log(clicked) 
                    if (clicked == 0){return 0.5;}
                    else if (clicked == 1){return 1;}
                    else if (clicked == 2) {return 0 ;};
                })
                .style("stroke-width", function(d){
                var clicked = d3.select('#'+d.handle).attr("clicked")
                //console.log(clicked) 
                    if (clicked == 0){return 3;}
                    else if (clicked == 1){return 1.5;}
                    else if (clicked ==2) {return 0 ;};
                });
            };

        function addNode(clickedNode){


            var cNode = d3.select(clickedNode).node() ;//why?? why not just clicked
            var contact = ['mentions', 'retweets'];


            for (var i=0; i<contact.length; i++){

                updateDisplayedNodes()

                for (twirpContact in cNode[contact[i]]){   //retweets and mentions separately
                    
                    if (displayedHandles[twirpContact] == undefined){  //only add new nodes
                        
                        for (j=0;j<map.nodes.length; j++){   
                            
                            if (map.nodes[j].handle == twirpContact &&
                                cNode[contact[i]][twirpContact]>10){ //should add global variable for control
                                
                                console.log(tally);
                                displayedNodes.push(map.nodes[j]);
                                displayedInvisibleNodes.splice(displayedNodes.length, 0, map.nodes[j]);

                            };
                        };  
                    };
                };
            };

            click  = d3.select(this)
            if (click.attr("clicked") == 0){
                force.stop();
                calculateEdges(clickedNode);
                redraw();
                d3.select('#'+cNode.handle).attr("clicked", 2);
            };
        };


        function calculateEdges(clickedNode){

            updateDisplayedNodes()
            
            
            var cNode = d3.select(clickedNode).node();

            var contact = ['mentions', 'retweets'];

   
            for (j=0; j<contact.length; j++){
                
                for(var mentionHandle in cNode[contact[j]]){  //cycle through 'full data'
                    
                    if (mentionHandle in displayedHandles){  //only plot to displayed nodes
  
                        var s_index = displayedHandles[cNode.handle],  //
                            t_index = displayedHandles[mentionHandle];
                            
                        var s = displayedNodes[s_index],
                            t = displayedNodes[t_index],
                            i = {};
                        
                       // console.log(displayedHandles)
                       // console.log(s)

                        var invisibleEdgeA = {source : s, target : i },
                            invisibleEdgeB = {source : i, target : t }; 

                        var visibleEdge = [ s, i,  t, contact[j], cNode[contact[j]][mentionHandle]];

                        if (cNode[contact[j]][mentionHandle]>10 && s.handle!=t.handle){
                            displayedInvisibleNodes.push(i);
                            displayedEdges.push(visibleEdge);
                            displayedInvisibleEdges.push(invisibleEdgeA);
                            displayedInvisibleEdges.push(invisibleEdgeB); 


                        };       
                    };
                
                };
            };
            //console.log(displayedEdges)
            //});
           // console.log(displayedEdges);
            //displayedInvisibleNodes.forEach(function(d){console.log(d)});
        };






        force.on("tick", function(){
            link.attr("d", function(d){
                return "M" + d[0].x + "," + d[0].y
                    + "S" + d[1].x + "," + d[1].y
                    + " " + d[2].x + "," + d[2].y;
            });

            node.attr("transform", function(d) {
                var r = 10 + (d.tweets/5000);
                return "translate("+ Math.max(r, Math.min(width-r, d.x)) + ","
                                   + Math.max(r, Math.min(width-r, d.y)) + ")";
            });
                
        });
    });



})();