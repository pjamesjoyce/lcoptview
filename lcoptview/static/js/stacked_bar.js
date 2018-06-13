//set up global absolute variables
// first the size and margins

var stack_bar_margin = {top: 50, right: 250, bottom: 20, left: 75},
	stack_bar_dimensions = {height:400, width: 750},
	stack_bar_width = stack_bar_dimensions.width - stack_bar_margin.left - stack_bar_margin.right,
	stack_bar_height = stack_bar_dimensions.height - stack_bar_margin.top - stack_bar_margin.bottom;

var legend_dimensions = {width:150, height:stack_bar_height};

// set the ranges
var stack_xScale = d3.scaleBand()
          .range([0, stack_bar_width])
          .padding(0.1);
var stack_yScale = d3.scaleLinear()
          .range([stack_bar_height, 0]);


//set the colour scale
var stack_color = d3.scaleOrdinal(d3.schemeCategory20);

var stack_svg;

function setup_stack_bar(){

	// append the stack_svg object to the #bar div
	// append a 'group' element to 'stack_svg'
	// moves the 'group' element to the top left margin
	stack_svg = d3.select("#stackedbar").append("svg")
		.attr("id", "stackedbar_svg")
	    .attr("width", stack_bar_dimensions.width)
	    .attr("height", stack_bar_dimensions.height)
	  .append("g")
	    .attr("transform", 
	          "translate(" + stack_bar_margin.left + "," + stack_bar_margin.top + ")");

	// add the x Axis
	stack_svg.append("g")
		.attr("class", "stack_xAxis")
	    .attr("transform", "translate(0," + stack_bar_height + ")")
	    .call(d3.axisBottom(stack_xScale));
	// add the y Axis
	stack_svg.append("g")
		.attr("class", "stack_yAxis")
	    .call(d3.axisLeft(stack_yScale));  

	stack_svg.append("text")
	    .attr("class", "y label")
	    .attr("id", "s_bar_yaxis_label")
	    .attr("text-anchor", "end")
	    .attr("y", 6)
	    .attr("dy", ".75em")
	    .attr("transform", "rotate(-90)")
	    .text("");

	/*stack_svg.append("g")
		.attr("class", "legend")
		.attr("transform", 
	          "translate(" + (stack_bar_width - legend_dimensions.width) + "," + (stack_bar_height + 25) + ")");
*/
	stack_svg.append("g")
	  .attr("class", "legendNew")
	  .attr("transform", 
	  	"translate(" + (stack_bar_width) + "," + 0 + ")");

		parsed_data = parse_stack_data();
	stack_bar_data = parsed_data[0];
	item_names = parsed_data[1];
	stackMax = parsed_data[2];

	stack_xScale.domain(stack_bar_data.map(function(d) { return d.name; }));
	stack_yScale.domain([0, stackMax]);
	
	stack_color.domain(item_names);


// DATA JOIN
  // Join new data with old elements, if any
	var bars = stack_svg.selectAll(".stack_bar")
		.data(stack_bar_data);
		// UPDATE
  		// Update old elements as needed.
  	bars
  		.attr("y", function(d) { return stack_yScale(stackMax); })
  		.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

	// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.

	bars.enter().append('g')
		.attr('class', 'stack_bar')
		.attr('x', function(d){ return stack_xScale(d.name);})
		.attr("y", function(d) { return stack_yScale(stackMax); })
		.attr("width", stack_xScale.bandwidth())
		.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

	//.merge(bars)
	//	.attr("y", function(d) { return stack_yScale(stackMax); })
  	//	.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
	//	.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

// EXIT
  // Remove old elements as needed.

  	bars.exit().remove();	

	update_stack_bar_2();
	//update_stack_bar();

}

function parse_stack_data(){
	var ps = $('#parameterSetChoice').val() - 1;
  	var m = $('#methodChoice').val() - 1;
  	var cutoff = 0.1;

	ps_length = bound_data.results.length;

	var table_data = [];
	var item_names = [];
	var cell_width = 100;

	for(var i = 0; i<ps_length; i++){
		var foreground_results = bound_data.results[i][m].foreground_results;
		
		var row_data = [];
		
		for(var data_row in foreground_results){

			var running_total=0;

			for(var p=0; p<ps_length; p++){
				//console.log(bound_data.results[p][m].foreground_results[data_row]);
				//console.log(bound_data.results[p][m].score);
				if(Math.abs(bound_data.results[p][m].foreground_results[data_row])/bound_data.results[p][m].score >= cutoff){
					running_total += Math.abs(bound_data.results[p][m].foreground_results[data_row]);
				}
			}
			//console.log(running_total);
			if(running_total != 0){
				row_data.push({label: data_row, value:foreground_results[data_row], rt:running_total});	
			}
		}
		row_data.sort(function(a, b) {
		    return parseFloat(b.rt) - parseFloat(a.rt);
		});

		table_data.push(row_data);
	}
	
	

	for(var col in table_data){
		previous_total = 0;
		for(var row in table_data[col]){
			table_data[col][row].previous = previous_total;
			previous_total += table_data[col][row].value;
			if (item_names.indexOf(table_data[col][row].label) < 0) {
				    item_names.push(table_data[col][row].label);
				}
		}
		table_data[col].push({
			label: 'Remaining items',
			value: bound_data.results[col][m].score - previous_total,
			previous: previous_total
		});
	} 

	item_names.push('Remaining items');
	stack_bar_data = [];

	for(var this_set in table_data){
		stack_bar_data.push({
			name: bound_data.results[this_set][m].ps_name,
			data: table_data[this_set]
		});
	}

	console.log(stack_bar_data);
	console.log(item_names);

	var stackTotals = [];

	for (var x in stack_bar_data){

		var t = 0;

		for (var i in stack_bar_data[x].data){
			t+= stack_bar_data[x].data[i].value;
		}
		stackTotals.push(t);
	} 

	stackMax = stackTotals.reduce(function(a, b) {
	    return Math.max(a, b);
	});
	
	console.log(stackMax);

	return [stack_bar_data, item_names, stackMax];
}


function update_stack_bar_2(){

	parsed_data = parse_stack_data();
	stack_bar_data = parsed_data[0];
	item_names = parsed_data[1];
	stackMax = parsed_data[2];

	console.log(stack_bar_data);

	/*stack_xScale.domain(stack_bar_data.map(function(d) { return d.name; }));
	stack_yScale.domain([0, stackMax]);
	
	stack_color.domain(item_names);


// DATA JOIN
  // Join new data with old elements, if any
	var bars = stack_svg.selectAll(".stack_bar")
		.data(stack_bar_data);
		// UPDATE
  		// Update old elements as needed.
  	bars
  		.attr("y", function(d) { return stack_yScale(stackMax); })
  		.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

	// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.

	bars.enter().append('g')
		.attr('class', 'stack_bar')
		.attr('x', function(d){ return stack_xScale(d.name);})
		.attr("y", function(d) { return stack_yScale(stackMax); })
		.attr("width", stack_xScale.bandwidth())
		.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

	//.merge(bars)
	//	.attr("y", function(d) { return stack_yScale(stackMax); })
  	//	.attr("height", function(d) { return stack_bar_height - stack_yScale(stackMax); })
	//	.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

// EXIT
  // Remove old elements as needed.

  	bars.exit().remove();	

*/
// DATA JOIN
  // Join new data with old elements, if any
  	var bars = stack_svg.selectAll(".stack_bar");
	var sections = bars.selectAll('.section');
		//sections.remove();
		sections
		.data(function(d){ return d.data; });
		// UPDATE
  		// Update old elements as needed.
  	sections
  		.transition()
  		.attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	    .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); });


	// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.
	sections.enter().append("rect")
	    .attr("class", "section")
	    .attr("title", function(d){ return d.label;})
	    .attr("data-legend", function(d){ return d.label ;})
	    .attr("fill", function(d){return stack_color(d.label);})
	    //.attr("x", function(d,i) { //console.log(); return stack_xScale(d.label); })
	    .attr("width", stack_xScale.bandwidth())
	    .attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	    .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); })

	   .merge(sections).transition()

		  //.attr("x", function(d) { return stack_xScale(d.label); })
	      //.attr("width", stack_xScale.bandwidth())
	      .attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	      .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); });

	sections.exit().remove();

	/*
		

	stack_svg.select('.stack_xAxis')
		.call(d3.axisBottom(stack_xScale));

	stack_svg.select('.stack_yAxis')
		.call(d3.axisLeft(stack_yScale));

	//console.log(bound_data.results[0][m].unit)

	stack_svg.select('#s_bar_yaxis_label').text(bound_data.results[0][m].unit);

	


// new approach
  	

	var legend = d3.legendColor()
	  .labelFormat(d3.format(".2f"))
	  //.useClass(true)
	  .title("")
	  .titleWidth(100)
	  .scale(stack_color);
	  //.labels(function(d){console.log(d); return d.domain[d.i].split("'")[1]})
	  //.orient('horizontal');

	stack_svg.select(".legendNew")
	  .call(legend);
*/
	
}


$(document).ready(function(){
	 $('#stacked_bar_export_button').click(function(){
    export_StyledSVG('stackedbar_svg', 'stacked_bar.png', stack_bar_dimensions.height , stack_bar_dimensions.width);
  });
});