console.log(date_1.length);
console.log(date_1[1]);
console.log(stepcount_1[1]);

dataset = []
for(var i=0; i < date_1.length; i++) {
    dataset.push({'name': date_1[i], 'value': parseInt(stepcount_1[i])});
}
console.log(dataset)

// set the dimensions and margins of the graph
var margin = {top: 30, right: 30, bottom: 100, left: 70},
    width = 1400 - margin.left - margin.right,
    height = 450 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#chart")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// X axis
var x = d3.scaleBand()
  .range([ 0, width ])
  .domain(dataset.map(d => d.name))
  .padding(0.2);

svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x))
  .selectAll("text")
  .style("font-size", "13px")
  .attr('transform', function(d){
    if(dataset.length >= 14 && dataset[0].name.length >= 5 || dataset[0].name.length >= 13){
      return "rotate(-15)"
    }
  })
  .attr('y', 12)
  .style("text-anchor", function(d){
    if(dataset.length >= 14 && dataset[0].name.length >= 5 || dataset[0].name.length >= 13){
      return "end"
    }
    return "center"
  });

// Add Y axis
var y = d3.scaleLinear()
  .domain([0, d3.max(dataset, d => d.value)]).nice()
  .range([ height, 0]);
  
svg.append("g")
  .style("font-size", "12px")
  .call(d3.axisLeft(y));

  // gridlines in y axis function
function make_y_gridlines() {		
  return d3.axisLeft(y)
      .ticks(5)
}

// add the Y gridlines
svg.append("g")			
.attr("class", "grid")
.attr('fill','none')
.attr('stroke', '#DCDCDC')
.attr('stroke-width',0.1)
.attr('shape-rendering','crispEdges')
.call(make_y_gridlines()
    .tickSize(-width)
    .tickFormat("")
)

// Bars
svg.selectAll("rect")
    .data(dataset)
    .enter()
    .append("rect")
    .attr("x", d => x(d.name))
    .attr("y", d => y(d.value))
    .attr("width", x.bandwidth())
    .attr("height",  d => y(0) - y(d.value))
    .attr("fill", "#9BB7D4")

// X axis label:
  // svg.append("text")
  // .attr("x", (width / 2))             
  // .attr("y", height + margin.top + 50)
  // .attr("text-anchor", "middle")  
  // .style("font-size", "16px") 
  // .text(legend_value);

// Y axis label:
svg.append("text")
    .attr("text-anchor", "center")
    .attr("transform", "rotate(-90)")
    .attr("y", -margin.left+15)
    .attr("x", -margin.top-150)
    .style("font-size", "16px") 
    .text(y_value)

