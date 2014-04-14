var data = [
/* these come from an actual run */
{revision:"r1", classifier: "bayes", decoder: "last", f1: 0.243},
{revision:"r1", classifier: "bayes", decoder: "local", f1:0.285},
{revision:"r1", classifier: "bayes", decoder: "locallyGreedy", f1:0.248},
{revision:"r1", classifier: "bayes", decoder: "mst", f1:0.291},
{revision:"r1", classifier: "maxent", decoder: "last", f1:0.301},
{revision:"r1", classifier: "maxent", decoder: "local", f1:0.261},
{revision:"r1", classifier: "maxent", decoder: "locallyGreedy", f1:0.304},
{revision:"r1", classifier: "maxent", decoder: "mst", f1:0.379},

    /* these are fake */
{revision:"r2", classifier: "bayes", decoder: "last", f1: 0.343},
{revision:"r2", classifier: "bayes", decoder: "local", f1:0.385},
{revision:"r2", classifier: "bayes", decoder: "locallyGreedy", f1:0.348},
{revision:"r2", classifier: "bayes", decoder: "mst", f1:0.391},
{revision:"r2", classifier: "maxent", decoder: "last", f1:0.401},
{revision:"r2", classifier: "maxent", decoder: "local", f1:0.361},
{revision:"r2", classifier: "maxent", decoder: "locallyGreedy", f1:0.204},
{revision:"r2", classifier: "maxent", decoder: "mst", f1:0.579},

{revision:"r3", classifier: "bayes", decoder: "last", f1: 0.373},
{revision:"r3", classifier: "bayes", decoder: "local", f1:0.285},
{revision:"r3", classifier: "bayes", decoder: "locallyGreedy", f1:0.448},
{revision:"r3", classifier: "bayes", decoder: "mst", f1:0.291},
{revision:"r3", classifier: "maxent", decoder: "last", f1:0.201},
{revision:"r3", classifier: "maxent", decoder: "local", f1:0.561},
{revision:"r3", classifier: "maxent", decoder: "locallyGreedy", f1:0.404},
{revision:"r3", classifier: "maxent", decoder: "mst", f1:0.379},
    ]

ndx=crossfilter(data);

var revisionDim = ndx.dimension(function(d) {return d.revision; });
var classDim = ndx.dimension(function(d) {return d.classifier;});
var decoderDim = ndx.dimension(function(d) {return d.decoder;});
var group = decoderDim.group().reduceSum(dc.pluck("f1"));

revisionDim.filter("r1");
var classifiers = _.uniq(_.pluck(data, "classifier"));

classifiers.forEach(function(entry) {
    var chartsElm = document.getElementById("charts");
    var subChartElm = document.createElement('div');
    subChartElm.id =  "chart-" + entry;
    chartsElm.appendChild(subChartElm);
});

classifiers.forEach(function(entry) {
    var chart = dc.barChart("#chart-" + entry);
    classDim.filterAll();
    classDim.filter(entry);
    chart.width(500).height(400)
         .gap(75)
         .brush(false)
         .centerBar(true);
    chart.x(d3.scale.ordinal())
         .y(d3.scale.linear())
         .xAxisLabel("decoder (w. " + entry + " classifier)")
         .yAxisLabel("F1")
         .xUnits(dc.units.ordinal)
         .title(function(d) { return entry + "/" + d.key + ": " + d.value; })
         .dimension(decoderDim)
         .group(group);
    if (entry === "bayes") {
         chart.colors(["orange"]);
    }
    chart.render();
});

// FIXME: what I would like is some mechanism that lets me to
// select a revision and see what the scores are for that
// particular revision
var chart = dc.lineChart("#revision");
classDim.filterAll();
classDim.filter("maxent");
decoderDim.filterAll();
decoderDim.filter("mst");
chart.width(500).height(400)
     .brush(false);
chart.dimension(revisionDim)
     .x(d3.scale.ordinal())
     .y(d3.scale.linear())
     .xUnits(dc.units.ordinal)
     .xAxisLabel("revision")
     .yAxisLabel("maxent/mst F1")
     .group(revisionDim.group().reduceSum(dc.pluck("f1")));
chart.render();
