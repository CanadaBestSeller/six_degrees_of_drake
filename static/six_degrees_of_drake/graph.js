// GRAPH.JS REQUIRES:
// JQUERY
// D3JS

function Graph(defaultImageUrl,
               width,
               height,
               nodeRadius,
               borderStyle,
               stroke,
               strokeWidth,
               strokeOpacity,
               linkDistance,
               charge,
               textStyle,
               textOffsetX,
               textOffsetY) {
    // public vars
    this.defaultImageUrl    = defaultImageUrl || "http://33.media.tumblr.com/avatar_a3415e501f10_128.png";
    this.width              = width || 500;
    this.height             = height || 500;
    this.nodeRadius         = nodeRadius || 48;
    this.borderStyle        = borderStyle || "none";
    this.stroke             = stroke || "#0095dd";
    this.strokeWidth        = strokeWidth || "2px";
    this.strokeOpacity      = strokeOpacity || ".6";
    this.linkDistance       = linkDistance || 200;
    this.charge             = charge || -400;
    this.textStyle          = textStyle || "font-family: Helvetica, sans-serif";
    this.textOffsetX        = textOffsetX || 0;
    this.textOffsetY        = textOffsetY || 0;

    this.nodeData = [];
    this.linkData = [];

    // Needed for private functions within a class, otherwise the private function's
    // 'this' variable will refer to the global window instead of the instance object:
    // http://www.sitepoint.com/javascript-this-gotchas/
    var closure = this;

    var force = d3.layout.force()
        .nodes(this.nodeData)
        .links(this.linkData)
        .linkDistance(this.linkDistance)
        .charge(this.charge)
        .size([this.width, this.height])
        .on("tick", tick);

    var svg = d3.select("body").append("svg")
        .style("width", this.width)
        .style("height", this.height)
        .style("border-style", this.borderStyle)
        .style("border-color", this.stroke)
        .style("border-width", this.strokeWidth);

    var imageDefinitions = svg.append("defs").attr("id", "img-defs");

    var nodeSet = svg.selectAll(".node");
    var textSet = svg.selectAll(".text");
    var linkSet = svg.selectAll(".link");

    this.addLink = function(id1, id2, weight) {
        var node1 = $.grep(this.nodeData, function(n) { return n.id === id1; })[0];
        var node2 = $.grep(this.nodeData, function(n) { return n.id === id2; })[0];
        this.linkData.push({source: node1, target: node2, weight: 30});
        start();
    }

    this.addNode = function(id, name, imageUrl) {
        finalImageUrl = imageUrl || this.defaultImageUrl;
        n = {id:id, name:name, imageUrl:finalImageUrl};
        this.nodeData.push(n);

        var nodePattern = imageDefinitions.append("pattern")
            .attr("id", "node-pattern-" + id)
            .attr("height", 1)
            .attr("width", 1)
            .attr("x", "0")
            .attr("y", "0");

        nodePattern.append("image")
            .attr("height", this.nodeRadius*2)
            .attr("width", this.nodeRadius*2)
            .attr("xlink:href", finalImageUrl);

        start();
    }

    function start() {
        linkSet = linkSet.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });
        linkSet.enter().insert("line", ".node")
            .attr("stroke", closure.stroke)
            .attr("stroke-width", closure.strokeWidth)
            .attr("stroke-opacity", closure.strokeOpacity)
            .attr("class", "link");
        linkSet.exit().remove();

        nodeSet = nodeSet.data(force.nodes(), function(d) { return d.id;});
        nodeSet.enter().append("circle")
            .attr("r", closure.nodeRadius)
            .attr("stroke", closure.stroke)
            .attr("stroke-width", closure.strokeWidth)
            .attr("stroke-opacity", closure.strokeOpacity)
            .attr("class", function(d) { return "node " + d.id; })
            .attr("fill", function(d) { return "url(#node-pattern-" + d.id + ")"; })
            .call(force.drag);
        nodeSet.exit().remove();

        textSet = textSet.data(force.nodes(), function(d) { return d.id;});
        textSet.enter().append("text")
            .text(function(d) { return d.name; })
            .attr("style", closure.textStyle);
        textSet.exit().remove();

        force.start();
    }

    function tick() {
        nodeSet.attr("cx", function(d) { return d.x; })
               .attr("cy", function(d) { return d.y; });

        textSet.attr("transform", function(d) { 
            var x = d.x + closure.textOffsetX;
            var y = d.y + closure.textOffsetY;
            return "translate(" + x + "," + y + ")"; })

        linkSet.attr("x1", function(d) { return d.source.x; })
               .attr("y1", function(d) { return d.source.y; })
               .attr("x2", function(d) { return d.target.x; })
               .attr("y2", function(d) { return d.target.y; });
    }

    resize();
    d3.select(window).on("resize", resize);

    function resize() {
        width = window.innerWidth, height = window.innerHeight;
        svg.attr("width", width).attr("height", height);
        force.size([width, height]).resume();
    }
}
