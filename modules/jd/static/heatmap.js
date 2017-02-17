/**
 * This plugin extends Highcharts in two ways:
 * - Use HTML5 canvas instead of SVG for rendering of the heatmap squares. Canvas
 *   outperforms SVG when it comes to thousands of single shapes.
 * - Add a K-D-tree to find the nearest point on mouse move. Since we no longer have SVG shapes
 *   to capture mouseovers, we need another way of detecting hover points for the tooltip.
 */
(function (H) {
    var Series = H.Series,
        each = H.each;

    /**
     * Create a hidden canvas to draw the graph on. The contents is later copied over
     * to an SVG image element.
     */
    Series.prototype.getContext = function () {
        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
            this.canvas.setAttribute('width', this.chart.chartWidth);
            this.canvas.setAttribute('height', this.chart.chartHeight);
            this.image = this.chart.renderer.image('', 0, 0, this.chart.chartWidth, this.chart.chartHeight).add(this.group);
            this.ctx = this.canvas.getContext('2d');
        }
        return this.ctx;
    };

    /**
     * Draw the canvas image inside an SVG image
     */
    Series.prototype.canvasToSVG = function () {
        this.image.attr({ href: this.canvas.toDataURL('image/png') });
    };

    /**
     * Wrap the drawPoints method to draw the points in canvas instead of the slower SVG,
     * that requires one shape each point.
     */
    H.wrap(H.seriesTypes.heatmap.prototype, 'drawPoints', function () {

        var ctx = this.getContext();

        if (ctx) {

            // draw the columns
            each(this.points, function (point) {
                var plotY = point.plotY,
                    shapeArgs,
                    pointAttr;

                if (plotY !== undefined && !isNaN(plotY) && point.y !== null) {
                    shapeArgs = point.shapeArgs;

                    pointAttr = (point.pointAttr && point.pointAttr['']) || point.series.pointAttribs(point);

                    ctx.fillStyle = pointAttr.fill;
                    ctx.fillRect(shapeArgs.x, shapeArgs.y, shapeArgs.width, shapeArgs.height);
                }
            });

            this.canvasToSVG();

        } else {
            this.chart.showLoading('Your browser doesn\'t support HTML5 canvas, <br>please use a modern browser');

            // Uncomment this to provide low-level (slow) support in oldIE. It will cause script errors on
            // charts with more than a few thousand points.
            // arguments[0].call(this);
        }
    });
    H.seriesTypes.heatmap.prototype.directTouch = false; // Use k-d-tree
}(Highcharts));


function draw_heatmap(id, header, max_value, data)
{
	var start = new Date;

	params = {
		chart: {
			type: 'heatmap',
			margin: [60, 10, 80, 50]
		},

		title: {
			text: header,
			x: 40
		},

		xAxis: {
			title: {
				text: "Time",
				x: -250
			},
			type: 'datetime',
			labels: {
				align: 'left',
				x: 5,
				y: 14,
				format: '{value:%H:%M}'
			},
			showLastLabel: false,
			tickLength: 16
		},

		yAxis: {
			title: {
				text: "Nodes"
			},
			labels: {
				enabled: false
			},
			minPadding: 0,
			maxPadding: 0,
			startOnTick: false,
			endOnTick: false,
		},

		colorAxis: {
			stops: [
				[0, '#ff0000'],
				[1, '#00ff00']
			],
			min: 0,
			max: max_value,
			startOnTick: false,
			endOnTick: false,
			labels: {
				format: '{value}'
			}
		},

		series: [{
			nullColor: '#EFEFEF',
			colsize: 1,
			tooltip: {
				headerFormat: 'node-{point.y}: ',
				pointFormat: '<b>{point.value}</b>'
			},
			turboThreshold: Number.MAX_VALUE // #3404, remove after 4.0.5 release
		}]
	}

	params.series[0].data = data;
	Highcharts.chart(id, params);

	console.log('Rendered in ' + (new Date() - start) + ' ms'); // eslint-disable-line no-console
}
