// GRAPH.JS REQUIRES:
// JQUERY
// D3JS

function Graph(imageUrl, width, height, nodeRadius, stroke, strokeWidth, strokeOpacity, linkDistance, charge) {
    // public vars
    this.imageUrl = imageUrl || "http://33.media.tumblr.com/avatar_a3415e501f10_128.png";
    this.width = width || 500;
    this.height = height || 500;
    this.nodeRadius = nodeRadius || 48;
    this.stroke = stroke || "#0095dd";
    this.strokeWidth = strokeWidth || "2px";
    this.strokeOpacity = strokeOpacity || ".6";
    this.linkDistance = linkDistance || 200;
    this.charge = charge || -400;

    this.nodes = [];
    this.links = [];

    // Needed for private functions within a class, otherwise the private function's
    // 'this' variable will refer to the global window instead of the instance object:
    // http://www.sitepoint.com/javascript-this-gotchas/
    var closure = this;

    var force = d3.layout.force()
        .nodes(this.nodes)
        .links(this.links)
        .linkDistance(this.linkDistance)
        .charge(this.charge)
        .size([this.width, this.height])
        .on("tick", tick);

    var svg = d3.select("body").append("svg")
        .attr("width", this.width)
        .attr("height", this.height)
        .style("border-style", "solid")
        .style("border-color", this.stroke)
        .style("border-width", this.strokeWidth);

    var imageDefinitions = svg.append("defs").attr("id", "img-defs");

    var node = svg.selectAll(".node"),
        link = svg.selectAll(".link");

    this.addLink = function(id1, id2, weight) {
        var node1 = $.grep(this.nodes, function(n) { return n.id === id1; })[0];
        var node2 = $.grep(this.nodes, function(n) { return n.id === id2; })[0];
        this.links.push({source: node1, target: node2, weight: 30});
        start();
    }

    this.addNode = function(id, name) {
        n = {id:id, name:name, imageUrl:this.imageUrl};
        this.nodes.push(n);

        var nodePattern = imageDefinitions.append("pattern")
            .attr("id", "node-pattern-" + id)
            .attr("height", 1)
            .attr("width", 1)
            .attr("x", "0")
            .attr("y", "0");

        nodePattern.append("image")
            .attr("height", this.nodeRadius*2)
            .attr("width", this.nodeRadius*2)
            .attr("xlink:href", this.imageUrl);

        start();
    }

    function start() {
        link = link.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });
        link.enter().insert("line", ".node")
            .attr("stroke", closure.stroke)
            .attr("stroke-width", closure.strokeWidth)
            .attr("stroke-opacity", closure.strokeOpacity)
            .attr("class", "link");
        link.exit().remove();

        node = node.data(force.nodes(), function(d) { return d.id;});
        node.enter().append("circle")
            .attr("r", closure.nodeRadius)
            .attr("stroke", closure.stroke)
            .attr("stroke-width", closure.strokeWidth)
            .attr("stroke-opacity", closure.strokeOpacity)
            .attr("class", function(d) { return "node " + d.id; })
            .attr("fill", function(d) { return "url(#node-pattern-" + d.id + ")"; })
            .call(force.drag);
        node.exit().remove();

        force.start();
    }

    function tick() {
        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })

        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
    }
}

// Add sample nodes. Delete later
var g = new Graph();

g.addNode('1', 'name1');
g.addNode('2', 'name2');
g.addNode('3', 'name3');

g.addLink('1', '2');
g.addLink('3', '2');
g.addLink('1', '3');
