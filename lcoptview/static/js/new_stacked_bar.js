var bound_data

d3.json("../results.json", function(data) {
	var ps = 0,
		m = 0,
		cutoff = 0.05;
	bound_data = data
	new_stacked_bar(data, m, cutoff);
});

var color30_firing = ["#000000", "#aec7e8", "#ff7f0e", "#f7b6d2", "#2ca02c", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
                "#8c564b", "#c5b0d5", "#7f7f7f", "#ffbb78", "#ff9896", "#9467bd", "#aec7e8", "#e377c2", "#98df8a", "#404040", 
                "#e41a1c", "#377eb8", "#00bf7a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#8dd3c7",
                "#1abd44", "#923bc1", "#94d957", "#317dff", "#4f9100", "#d28aff", "#006f0c", "#a20083", "#ff9896"];//,"#00bf7a", "#c60040",];

var stack_color = d3.scaleOrdinal(color30_firing)

var stack_margin = {top: 10, bottom: 50, left: 50, right: 200},
  stack_width = 400 //window.innerWidth - margin.left - margin.right,
  stack_height = 400 //window.innerHeight - margin.top - margin.bottom;

var stack_x = d3.scaleBand()
.rangeRound([0, stack_width])
.padding(.1);

var stack_y = d3.scaleLinear()
    .rangeRound([stack_height, 0]);

function redraw_trigger(){
	m = $('#methodChoice').val() - 1;
	c  = $('#stack_cutoff').val() / 100; 
	redraw(bound_data, m, c);
}

function slugify(text)
{
  return text.toString().toLowerCase()
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-')         // Replace multiple - with single -
    .replace(/^-+/, '')             // Trim - from start of text
    .replace(/-+$/, '');            // Trim - from end of text
}

function parse_stack_data(data, m, cutoff) {

	//console.log(data);
	//console.log(m, cutoff);

  	ps_length = data.results.length;
  	ps_names = [];

  	percentages = [];
  	item_names = [];

  	for(var ps = 0; ps < ps_length; ps++){
  		ps_names.push(data.results[ps][m].ps_name);
  		var fr = data.results[ps][m].foreground_results;
  		//console.log(fr);
  		this_set = {};
  		for(var item in fr){
  			this_set[item] = fr[item]/data.results[ps][m].score;
  			if(item_names.indexOf(item) < 0){
  				item_names.push(item);
  			}
  		}
  		percentages.push(this_set);
  	}

  	//console.log(percentages);
  	//console.log(item_names);

  	include = [];
  	for(var item in item_names){
  		var item_name = item_names[item];

  		for (var ps = 0; ps < ps_length; ps++){
  			if(percentages[ps][item_name] >= cutoff){
  				include.push(item_name);
  				break;
  			}
  		}
  	}

  	to_stack = [];
  	ri_total = 0;

  	for(var ps = 0; ps < ps_length; ps++){
  		var stack_this_item = {};
  		stack_this_item.name = data.results[ps][m].ps_name;
  		total = data.results[ps][m].score;

  		var running_total = 0;
  		for(var item in item_names){
  			var item_name = item_names[item];
  			if(include.indexOf(item_name) >= 0){
  				var this_score = data.results[ps][m].foreground_results[item_name];
	  			stack_this_item[item_name]= this_score;
	  			running_total += this_score;
  			}  			
  			else
		  		{
		  			stack_this_item[item_name] = 0;
		  		}
	  	}
  		stack_this_item['Remaining items'] = total-running_total;
  		ri_total += total-running_total;
  		stack_this_item.sum = total;
  		to_stack.push(stack_this_item);
  	}

  	keys = item_names.concat("Remaining items");
  	
  	if(ri_total > 0){
  		legend = include.concat("Remaining items");
  	}else{
  		legend = include;
  	}

  	return [keys, to_stack, ps_names, legend];

}


function new_stacked_bar(data, m, cutoff){

	ps_length = data.results.length;
  	names = [];



  	for(var ps = 0; ps < ps_length; ps++){
  		names.push(data.results[ps][m].ps_name);
  	}

  	stack_x.domain(names);



    var stack_svg = d3.select("#stackedbar").append("svg")
        .attr("width", stack_width + stack_margin.left + stack_margin.right)
        .attr("height", stack_height + stack_margin.top + stack_margin.bottom)
      .append("g")
        .attr("transform", "translate(" + stack_margin.left + "," + stack_margin.top + ")")
        .attr("id", "stackedbar_svg");

       

    // add the x Axis
	stack_svg.append("g")
		.attr("class", "stack_xAxis")
	    .attr("transform", "translate(0," + stack_height + ")")
	    .call(d3.axisBottom(stack_x));
	// add the y Axis
	stack_svg.append("g")
		.attr("class", "stack_yAxis")
	    .call(d3.axisLeft(stack_y));

	stack_svg.append("g")
          .attr("class", "legendNew_sb")
          .attr("id", "stack_legend_box")
          .attr("transform", 
            "translate(" + stack_width + "," + 0 + ")")
          .attr("height", stack_height +"px");  
	
    stack_svg.append("text")
	    .attr("class", "y label")
	    .attr("id", "s_bar_yaxis_label")
	    .attr("text-anchor", "end")
	    .attr("y", 6)
	    .attr("dy", ".75em")
	    .attr("transform", "rotate(-90)")
	    //.style("font-size", "9px")
	    //.style("font-family", "Arial")
	    .text("placeholder");

	//var series = stack(stack_data);

	//console.log(series);        

	

    redraw(data, m, cutoff);

}

function redraw(data, m, cutoff){

    var stack_svg = d3.select("#stackedbar_svg")

    var stack = d3.stack()
	    .order(d3.stackOrderNone)
	    .offset(d3.stackOffsetNone);

      	parsed_data = parse_stack_data(data, m, cutoff);
		keys = parsed_data[0];
		stack_data = parsed_data[1];
		stack_legend = parsed_data[3];
		unit = data.results[0][m].unit;

	  stack.keys(keys);

      max_data = stack_data.map(function(d){return d.sum ;});
      //console.log(max_data)
      //var max_y = jz.arr.max(data.map(function(d){ console.log(d); return d.sum }));
      var max_y = Math.max.apply(null, max_data);

      stack_legend_data = [];
      stack_legend.forEach(function(d,i){
      	stack_legend_data.push({
      		label:d,
      		color:stack_color(d)
      	});
      });

      var stack_legend_box = stack_svg.select(".legendNew_sb");
      stack_legend_box.selectAll("*").remove();

      stack_legend_items = stack_legend_box.selectAll(".legend_item")
      	.data(stack_legend_data);

      this_l_item = stack_legend_items.enter().append("g")
      	.attr("class", "legend_item")
      	.attr("transform", function(d, i){ return "translate(0, " + (i * 12) + ")" ;});

      this_l_item.append("rect")
      	.attr("height", "10px")
      	.attr("width", "10px")
      	.attr("fill", function(d){ return d.color });

      this_l_item.append("text")
      	.attr("height", "10px")
      	.attr("width", "100px")
      	.attr("dy", "8px")
      	.attr("transform", "translate(12, 0)")
      	.style("font-size", "9px")
      	.style("font-family", "Arial")
      	.text(function(d){return d.label});


      // update the y scale
      stack_y.domain([0, max_y]);
      stack_svg.select(".stack_yAxis")
	    .call(d3.axisLeft(stack_y));  

	  stack_svg.select('#s_bar_yaxis_label').text(unit);

      // each data column (a.k.a "key" or "series") needs to be iterated over
      keys.forEach(function(key, key_index){

        var bar = stack_svg.selectAll(".bar-" + slugify(key))
            .data(stack(stack_data)[key_index], function(d){ return d.data.name + "-" + slugify(key); });

        bar
          .transition()
            .attr("x", function(d){ return stack_x(d.data.name); })
            .attr("y", function(d){ return stack_y(d[1]); })
            .attr("height", function(d){ return stack_y(d[0]) - stack_y(d[1]); });

        bar.enter().append("rect")
            .attr("class", function(d){ return "bar bar-" + slugify(key); })
            .attr("x", function(d){ return stack_x(d.data.name); })
            .attr("y", function(d){ return stack_y(d[1]); })
            .attr("height", function(d){ return stack_y(d[0]) - stack_y(d[1]); })
            .attr("width", stack_x.bandwidth())
            .attr("fill", function(d){ return stack_color(key); })

      });  
}