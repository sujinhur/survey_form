console.log(date_1.length);
console.log(date_1[1]);
console.log(stepcount_1[1]);

dataset = []
for(var i=0; i < date_1.length; i++) {
    dataset.push({'name': date_1[i], 'value': parseInt(stepcount_1[i])});
}
console.log(dataset)

// set the dimensions and margins of the graph
var margin = {top: 30, right: 30, bottom: 70, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

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
  .style("text-anchor", "center");

// Add Y axis
var y = d3.scaleLinear()
  .domain([0, d3.max(dataset, d => d.value)])
  .range([ height, 0]);
svg.append("g")
  .call(d3.axisLeft(y));

// Bars
svg.selectAll("rect")
    .data(dataset)
    .enter()
    .append("rect")
    .attr("x", d => x(d.name))
    .attr("y", d => y(d.value))
    .attr("width", x.bandwidth())
    .attr("height",  d => y(0) - y(d.value))
    .attr("fill", "#69b3a2")


  svg.append("text")
  .attr("x", (width / 2))             
  // .attr("y", 0 - (margin.top / 2))
  .attr("y", height + margin.top + 10)
  .attr("text-anchor", "middle")  
  .style("font-size", "16px") 
  .text(legend_value);

