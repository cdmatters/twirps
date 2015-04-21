;(function(){
    var width = 1000,
        height =  680;

    var force = d3.layout.force()
        .linkDistance(10)
        .linkStrength(2)
        .size([width, height])
        .gravity(0.8);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    var color = d3.scale.category20();

    d3.json("map_d3.json", function(error, graph) {
        var nodes = graph.nodes.slice(),
            links = [],
            bilinks = [];

        graph.links.forEach(function(link) {

            var s = nodes[link.source],  
                t = nodes[link.target],
                i = {};

            nodes.push(i);  //adds an intermediate node for each link
            links.push({source:s, target:i, contact:link.contact});
            links.push({source:t, target:t, contact:link.contact});
            bilinks.push({source:s, inter:i, target:t, contact:link.contact});

        });

        force
            .nodes(nodes)
            .links(links)
            .start();

        var node = svg.selectAll(".node")
            .data(graph.nodes.slice(2,10)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 5)
            .attr("party", function(d){return d.party;})
            .style("fill", function(d) { return color(d.party_no); })
            .call(force.drag)
            .on("click", addLinks(this, link));
            
        
        function addLinks(thisNode, links){
            for (i=0; i<bilinks.length; i++ ){
                if (bilinks[i].source == nodes.indexOf(thisNode)){
                    console.log(bilinks[i].source);
                    var link = svg.selectAll(".link")
                        .data(bilinks)
                        .enter().append("path")
                        .attr("class", "link")
                        .attr("stroke-width", 1)
                        .attr("contact", function(d){d[3]})
                }
                console.log(i)
            }
            return false;
        };

        node.append("title")
            .text(function(d) { return d.name; });

        var link = svg.selectAll(".link")
            

        console.log(node)

        force.on("tick", function() {
            link.attr("d", function(d) {
              return "M" + d[source].x + "," + d[source].y
                  + "S" + d[inter].x + "," + d[inter].y
                  + " " + d[target].x + "," + d[target].y;
            });
            node.attr("transform", function(d) {
              return "translate(" + d.x + "," + d.y + ")";
            });
        })
    });

})();