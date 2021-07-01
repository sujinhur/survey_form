legend_value = JSON.parse(legend_value);

// 쿼리 결과 값 저장 변수
dataset = [];
dataset1 = [];


for(var i=0; i < date_1.length; i++) {
    dataset.push({'name': date_1[i], 'value': parseInt(stepcount_1[i])});
}
for(var i=0; i < date_2.length; i++) {
    dataset1.push({'name': date_2[i], 'value': parseInt(stepcount_2[i])});
}


// y축 ticks 설정
data_max = [];
data_max.push({'value' : d3.max(dataset, d => d.value)});
data_max.push({'value' : d3.max(dataset1, d => d.value)});

data_min = [];
data_min.push({'value' : d3.min(dataset, d => d.value)});
data_min.push({'value' : d3.min(dataset1, d => d.value)});


// 기본적인 마진값
var margin = {top: 10, right: 30, bottom: 60, left: 100},
    width = 1000 - margin.left - margin.right,
    height = 450 - margin.top - margin.bottom

// canvas 사이즈
var svg = d3
  .select("#chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)

// graph 사이즈
var graph = svg
  .append("g")
  .attr("width", width)
  .attr("height", height)
  .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// 축 범위 설정
var x = d3
  .scaleBand()
  .domain(dataset1.map(d => d.name))
  .range([ 0, width ])
  .padding(0.5);

var y = d3
  .scaleLinear()
  .domain([d3.min(data_min, d => (d.value/100)*90), d3.max(data_max, d => (d.value/100)*105)]).nice()
  .range([ height, 0 ]);

// axis groups
const xAxisGroup = graph
  .append("g")
  .attr("class", "x-axis")
  .style("font-size", "14px")
  .attr("transform", "translate(0," + height + ")");

const yAxisGroup = graph
  .append("g")
  .style("font-size", "12px")
  .attr("class", "y-axis");

// create axes
const xAxis = d3
  .axisBottom(x)
  .ticks(5)

const yAxis = d3
  .axisLeft(y)

// call axes
xAxisGroup.call(xAxis);
yAxisGroup.call(yAxis);


// d3 Line path generator *****
var line = d3
  .line()
  .x(function(d) {
    return x(d.name);
  })
  .y(function(d) {
    return y(d.value);
  });

// line path element
var path = graph.append("path");

// update line path data *****
path
.attr("d", line(dataset)) 
.attr("fill", "none")
.attr("stroke", "#E0808F")
.attr("stroke-width", 3);

var line1 = d3
  .line()
  .x(function(d) {
    return x(d.name);
  })
  .y(function(d) {
    return y(d.value);
  });

// line path element
var path1 = graph.append("path");

// update line path data *****
path1
.attr("d", line1(dataset1)) 
.attr("fill", "none")
.attr("stroke", "#5192C6")
.attr("stroke-width", 3);

// 범례 표시
colors = ["#E0808F", "#5192C6"];
var legend = svg.append("g")
    .attr("text-anchor", "end")
    .selectAll("g")
    .data(legend_value)
    .enter().append("g")
    .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

legend.append("rect")
    .attr("x", width)
    .attr("y", 10)
    .attr("width", 20)
    .attr("height", 13)
    .attr("fill", function(d, i) { return colors[i]; });

legend.append("text")
    .attr("x", width -5)
    .attr("y", 20)
    .attr("dy", "0.01em")
    .attr("font-size", "12px")
    .text(function(d) { return d; });

// Y axis label:
svg.append("text")
  .attr("text-anchor", "center")
  .attr("transform", "rotate(-90)")
  .attr("y", -margin.left + 140)
  .attr("x", -margin.top-200)
  .style("font-size", "16px") 
  .text(y_value)