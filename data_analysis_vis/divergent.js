//with thanks to MBostock's divergent force graph example, 
//from which this is adapated [http://bl.ocks.org/mbostock/1021841]
;(function(){
    var width = 1000,
        height = 800;

    var fill = d3.scale.category10();



    d3.json('kmeans_naive.json', function(data){ 
        var nodes = data
    

        var force = d3.layout.force()
            .nodes(nodes)
            .size([width, height])
            .on("tick", tick)
            .start();

        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

        var node = svg.selectAll(".node")
            .data(nodes)
          .enter().append("circle")
            .attr("class", "node")
            .attr("id", function(d) { return d.name})
            .attr("cluster", function(d) {return d.cluster})
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })
            .attr("r", 8)
            .style("fill", function(d) { return fill(d.cluster); })
            .style("stroke", function(d) { return d3.rgb(d.cluster).darker(2); })
            .call(force.drag)
            .on("mousedown", function() { d3.event.stopPropagation(); });
        node.append("title")
            .text(function(d){return d.name;});


        svg.style("opacity", 1e-6)
          .transition()
            .duration(1000)
            .style("opacity", 1);

        d3.select("body")
            .on("mousedown", mousedown);

        function tick(e) {

          // Push different nodes in different directions for clustering.
          var k = 6 * e.alpha;
          nodes.forEach(function(o, i) {
            console
            o.y += o.cluster & 1 ? k : -k;
            o.x += o.cluster & 2 ? k : -k;
          });

          node.attr("cx", function(d) { return d.x; })
              .attr("cy", function(d) { return d.y; });
        }

        function mousedown() {
          nodes.forEach(function(o, i) {
            o.x += (Math.random() - .5) * 20;
            o.y += (Math.random() - .5) * 20;
          });
          force.resume();
        }

    });

})();