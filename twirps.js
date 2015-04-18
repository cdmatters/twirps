;(function(){

    var width = 960, 
        height =600;

    var color = d3.scale.category20()

    var force = d3.layout.force()
        .charge(-50)
        .linkDistance(100)
        .size([width, height]);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    //mapData = JSON.parse('map.json')
    //console.log(JSON.stringify(mapData, null, 2))
    d3.json('map_d3.json', function(error, map){
        force
            .nodes(map.nodes)
            .links(map.links)
            .start();

        var link = svg.selectAll(".link")
            .data(map.links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width",   1);

        var node = svg.selectAll(".node")
            .data(map.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 5)
            .style("fill", function(d){return color(d.party_no);})
            .call(force.drag)
            .on("click",  function(){console.log('yo');});


        node.append("title")
            .text(function(d){return d.name;});


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