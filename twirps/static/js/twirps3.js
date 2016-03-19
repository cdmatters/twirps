;(function(){

    var map_url=  $SCRIPT_ROOT + '/string';

    var width = 2000, 
        height =1200;

    var parties_map= {"Conservative":"#0575c9", "Labour":"#ed1e0e",
        "Liberal Democrat":"#fe8300", "UKIP":"#712f87", "Green":"#78c31e",
        "Scottish National Party":"#EBC31C", "Social Democratic and Labour Party":"#65a966",
        "DUP":"#c0153d", "Sinn Fein":"#00623f", "Alliance":"#e1c21e", "Respect":"#31b56a",
        "Plaid Cymru":"#4e9f2f", "Independent":"#4e9f2f", "UUP":"#4e9f2f"
         };

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
        clickedNodes =[],
        lastCursor;
        toggle = {radius:false, highlight:false};

    
    d3.json(map_url, function(error, map){
        
        displayedNodes = map.nodes.slice();
        displayedInvisibleNodes = displayedNodes.slice()

        
        d3.select("body").on("keypress", keyController );
        var displayedHandles = {};
        var link;
        var node;
        
        updateDisplayedNodes();
        redrawMap();
        


        function updateDisplayedNodes(){
            
            displayedNodes.forEach(
                function(d){ displayedHandles[d.handle] = displayedNodes.indexOf(d)}
            );
        }

        function keyController(){
            var key = d3.event.keyCode;

            if (key == 116){ radiusTransition();}
            else if (key == 32){ 
                toggle.highlight = (!toggle.highlight);
                highlightTransition();
                }
        };
        
        function redrawMap(){
            d3.selectAll('svg').remove();

            svg = d3.select("body").append("svg")
                .attr("width", width)
                .attr("height", height);

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
                .style("stroke-opacity", 0.5)
                .style("stroke", function(d){
                 // console.log(d[3])
                  if (d.contact=='mentions'){
                    //console.log('hey')
                    return 'grey';}
                  else {
                    return 'black';};
                   })
                .style("marker-end", "url(#end)")

            svg.append("defs").selectAll("marker")
                .data(displayedEdges.map(function(d){return d.source.handle}))
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
                .attr("class", function(d){return d})
                .style("stroke", function(d){
                 // console.log(d[3])
                  if (d.contact=='mentions'){
                    //console.log('hey')
                    return 'grey';}
                  else{ 
                    return 'black';};
                   })
                .style("stroke-opacity",0.5);

            node = svg.selectAll(".node")
                .data(displayedNodes)
              .enter().append("g") 
                .attr("class", "node")
                .call(force.drag)
                .attr("id", function(d){return d.handle;})
            node.append("circle")
                .attr("clicked", 0)
                .attr("fill", function(d) {return parties_map[d.party]; })
                .style("stroke", 'white' )
                .attr("party", function(d){return d.party})
                .on("click", addNode)
            node.append("text")
                .attr("dx", -25)
                .attr("dy", 5)
                .text(function(d){return })
                .style("stroke", "black");
            node.append("title")
                .text(function(d){return d.name;});
                

                
            clickedNodes.forEach(function(d){
                d3.select('#'+d).selectAll('circle').attr("clicked", 1)
            });            

            

            node.selectAll("circle")
                .style("stroke-opacity", function(d){
                    var clicked = d3.select('#'+d.handle).selectAll('circle').attr("clicked");
                    if (clicked == 0){return 0.5;}
                    else if (clicked == 1){return 1;};
                })
                .style("stroke-width", function(d){
                    var clicked = d3.select('#'+d.handle).selectAll('circle').attr("clicked");
                    if (clicked == 0){return 3;}
                    else if (clicked == 1){return 1.5;};
                })
                .attr("r", function(d){
                    var clicked = d3.select('#'+d.handle).selectAll('circle').attr("clicked");
                    if (clicked == 1 && toggle.radius==true){return 5 + Math.sqrt(d.tweets/100);}
                    else{return 5;}; 
                });
            node.selectAll("text")
                .text( function(d){
                    var clicked = d3.select('#'+d.handle).selectAll('circle').attr("clicked");
                    if (clicked == 1 && toggle.radius==true){return d.name;}
                    else{return};
                })

            highlightTransition();



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
                                
                                //console.log(tally);
                                displayedNodes.push(map.nodes[j]);
                                displayedInvisibleNodes.splice(displayedNodes.length, 0, map.nodes[j]);

                            };
                        };  
                    };
                };
            }

            click  = d3.select(this);
            lastCursor = click.node();
            highlightTransition() 
            
            if (click.attr("clicked") == 0){
                clickedNodes.push(click[0][0].__data__.handle)
                force.stop();
                calculateEdges(clickedNode);
                redrawMap();
                d3.select('#'+cNode.handle).attr("clicked", 2);
            };
        };
        function calculateEdges(clickedNode){
            console.log("were here")
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

                        var visibleEdge = {source:s, inter:i, target:t, contact:contact[j], value:cNode[contact[j]][mentionHandle]};

                        if (visibleEdge.value>0 && s.handle!=t.handle){
                            displayedInvisibleNodes.push(i);
                            displayedEdges.push(visibleEdge);
                            displayedInvisibleEdges.push(invisibleEdgeA);
                            displayedInvisibleEdges.push(invisibleEdgeB); 
                        };       
                    };  
                };
            };
        };
        function radiusTransition(){

            if (toggle.radius == false){
                clickedNodes.forEach( function(handle){
                    d3.select("#"+handle).selectAll('circle')
                        .transition()
                        .duration(2000)
                        .attr("r", function(d){return 5+ Math.sqrt(d.tweets/100);});
                    d3.select("#"+handle).selectAll('text')
                        .text(function(d){return d.name})
                });
                toggle.radius = true;
            } else if (toggle.radius == true){
                clickedNodes.forEach( function(handle){
                    d3.select("#"+handle).selectAll('circle')
                        .transition()
                        .duration(2000)
                        .attr("r", 5);
                });
                node.selectAll('text')
                    .text(function(){return;});

                toggle.radius = false;
            };            
        };

        function highlightTransition(){

            if (lastCursor != undefined){
                if (toggle.highlight == true){
                    var highlightedNodes = [lastCursor.__data__.handle];

                    displayedEdges.forEach( function(d){
                        if (d.source.handle == lastCursor.__data__.handle){
                            highlightedNodes.push(d.target.handle);
                        };
                    });

                    node.selectAll("circle")
                        .transition()
                        .duration(1000)
                        .attr('opacity', function(d){
                            if (highlightedNodes.some(function(e){return d.handle==e;})){
                                return 1;
                            } else {return 0.1;}
                        });
                    node.selectAll("text")
                        .transition()
                        .duration(3000)
                        .text(function(d){
                            if (highlightedNodes.some(function(e){return d.handle==e;}) && toggle.radius == true){
                                return d.name;
                            } else {return;}
                        });
                    link.style('stroke-opacity', function(d){
                            if (d.source.handle == lastCursor.__data__.handle) {return 1;}
                            else {return 0.05} })
                    svg.selectAll("marker").selectAll("path")
                            .style("stroke-opacity", 0.05);

                    //console.log(svg.selectAll("."+lastCursor.__data__.handle).style("stroke-opacity", 1))

                    

                } else if (toggle.highlight == false){

                    node.selectAll("circle")
                        .transition()
                        .duration(1000)
                        .attr('opacity', 1)
                    node.selectAll("text")
                        .text(function(){return})
                    if (toggle.radius == true){
                        clickedNodes.forEach( function(handle){  
                            d3.select("#"+handle).selectAll('text')
                               .text(function(d){return d.name})
                        });
                    };
                    link.style('stroke-opacity', 0.5) ;
                    svg.selectAll("marker").selectAll("path")
                            .style("stroke-opacity", 0.5); 
        
                    
                };

            };  
        };







        force.on("tick", function(){

            function border(z, axis ){
                var r = 5; 
                if (axis == 'x'){return Math.max(2*r, Math.min(width-2*r, z))}
                else if (axis == 'y'){return Math.max(2*r, Math.min(height-2*r, z))};
            }

            link.attr("d", function(d){
                return "M" + border(d.source.x,'x') + "," + border(d.source.y,'y')
                    + "S" + border(d.inter.x,'x') + "," + border(d.inter.y,'y')
                    + " " + border(d.target.x,'x') + "," + border(d.target.y,'y');
            });

            node.attr("transform", function(d) {
                var r = 5
                return "translate("+ border(d.x,'x') + ","
                                   + border(d.y,'y') + ")";
            });
                
        });
    });



})();