// Dimensions
var RECT_WIDTH = 150;
var RECT_HEIGHT = 100;
var ELLIPSE_RX = 90;
var ELLIPSE_RY = 60;

// Link label placement
var TOP = 1;
var RIGHT = 2;
var BOTTOM = 3;
var LEFT = 4;

// Canvas
var paper = Raphael(document.getElementById("neighbour_view"), 710, 505);


function addReport(x, y, title, uri, nativeId) {
	var pathStr = "M " + x + "," + y +
		" L " + (x+RECT_WIDTH) + "," + y +
		" L " + (x+RECT_WIDTH) + "," + (y+RECT_HEIGHT - 10)	+
		" L " + (x+RECT_WIDTH-10) + "," + (y+RECT_HEIGHT) +
		" L " + x + "," + (y+RECT_HEIGHT) +
		" L " + x + "," + y;
	var report = paper.path(pathStr);
	report.attr({fill: "90-#DF0101-#FE2E2E", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "Report", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, uri, 12, null, 2, "#000000");
	if(nativeId && nativeId != "")
	    addTextLabel(x + (RECT_WIDTH/2), y + (4 * RECT_HEIGHT / 5), RECT_WIDTH, nativeId, null, 12, null, 1, "#FFFFFF");
	report.glow();
	return report;
}


function addEntity(cx, cy, title, uri) {
	var entity = paper.ellipse(cx, cy, ELLIPSE_RX, ELLIPSE_RY);
	entity.attr({fill: "90-#D7DF01-#F7FE2E", stroke: "#000000", "stroke-width": 1});
	addTextLabel(cx, cy - (ELLIPSE_RY / 2), ELLIPSE_RX*2, "Entity", null, 16, "bold", 1, "#000000");
	addTextLabel(cx, cy, ELLIPSE_RX*2, title, uri, 12, null, 2, "#000000");
	entity.glow();
	return entity;
}


function addActivity(x, y, title, uri) {
	var activity = paper.rect(x, y, RECT_WIDTH, RECT_HEIGHT);
	activity.attr({fill: "90-#00BFFF-#81DAF5", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "Activity", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, uri, 12, null, 2, "#000000");
	activity.glow();
	return activity;
}


function addReportingSystem(x, y, title, uri) {
	var pathStr = "M " + (x+20) + "," + y +
		" L " + (x+RECT_WIDTH-20) + "," + y +
		" L " + (x+RECT_WIDTH) + "," + (y+20) +
		" L " + (x+RECT_WIDTH) + "," + (y+RECT_HEIGHT-20) +
		" L " + (x+RECT_WIDTH-20) + "," + (y+RECT_HEIGHT) +
		" L " + (x+20) + "," + (y+RECT_HEIGHT) +
		" L " + x + "," + (y+RECT_HEIGHT-20) +
		" L " + x + "," + (y+20) +
		" L " + (x+20) + "," + y;
	var rs = paper.path(pathStr);
	rs.attr({fill: "90-#DF01A5-#FE2EC8", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "ReportingSystem", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, uri, 12, null, 2, "#000000");
    rs.glow();
	return rs;
}


function addAgent(x, y, title, uri) {
	var pathStr = "M " + x + "," + (y+20) +
		" L " + (x+RECT_WIDTH/2) + "," + y +
		" L " + (x+RECT_WIDTH) + "," + (y+20) +
		" L " + (x+RECT_WIDTH) + "," + (y+RECT_HEIGHT) +
		" L " + x + "," + (y+RECT_HEIGHT) +
		" L " + x + "," + (y+20);
	var agent = paper.path(pathStr);
	agent.attr({fill: "90-#DF7401-#FE9A2E", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "Person", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, uri, 12, null, 2, "#000000");
    agent.glow();
	return agent;
}


function addValue(x, y, title) {
	var value = paper.rect(x, y, RECT_WIDTH, RECT_HEIGHT);
	value.attr({fill: "90-#A4A4A4-#E6E6E6", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "Value", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, "", 12, null, 2, "#000000");
	value.glow();
	return value;
}


function addLinkedActivity(x, y, title, uri) {
	var activity = paper.rect(x, y, RECT_WIDTH, RECT_HEIGHT);
	activity.attr({fill: "90-#006BFF-#00BFFF", stroke: "#000000", "stroke-width": 1});
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 4), RECT_WIDTH, "Activity", null, 16, "bold", 1, "#000000");
	addTextLabel(x + (RECT_WIDTH/2), y + (RECT_HEIGHT / 2), RECT_WIDTH, title, uri, 12, null, 2, "#000000");
	activity.glow();
	return activity;
}


function addLink(obj1, obj2, label, position) {
    bb1 = obj1.getBBox();
    bb2 = obj2.getBBox();
	x1Centre = bb1.x + (bb1.width/2),
	x2Centre = bb2.x + (bb2.width/2);
	y1Centre = bb1.y + (bb1.height/2);
	y2Centre = bb2.y + (bb2.height/2);
	xDiff = Math.max(x1Centre, x2Centre) - Math.min(x1Centre, x2Centre);
	yDiff = Math.max(y1Centre, y2Centre) - Math.min(y1Centre, y2Centre);
	x1 = x1Centre;
	y1 = y1Centre;
	x2 = x2Centre;
	y2 = y2Centre;
	if (xDiff >= yDiff) {
	    if (bb1.x < bb2.x) {
	        x1 = bb1.x + bb1.width;
	        y1 = bb1.y + (bb1.height/2);
            x2 = bb2.x;
            y2 = bb2.y + (bb2.height/2);
	    } else {
            x1 = bb1.x;
            y1 = bb1.y + (bb1.height/2);
            x2 = bb2.x + bb2.width;
	        y2 = bb2.y + (bb2.height/2);
	    }
	} else {
        if (bb1.y < bb2.y) {
	        x1 = bb1.x + (bb1.width/2);
	        y1 = bb1.y + bb1.height;
            x2 = bb2.x + (bb2.width/2);
            y2 = bb2.y;
	    } else {
	        x1 = bb1.x + (bb1.width/2);
            y1 = bb1.y;
	        x2 = bb2.x + (bb2.width/2);
	        y2 = bb2.y + bb2.height;
	    }
	}
    var path = "M " + x1 + "," + y1 + " L " + x2 + "," + y2;
	var line = paper.path(path);
    line.attr({"stroke-width": 3, "arrow-end": "classic-wide-long"})

    if(label == null)
        label = "";
    // Text dimensions
    var tX = line.getBBox().x + (line.getBBox().width/2);
    var tY = line.getBBox().y + (line.getBBox().height/2);
    var lineLabel = paper.text(tX, tY, label);
    lineLabel.attr({"font-size": 12});
    var tW = lineLabel.getBBox().width;
    var tH = lineLabel.getBBox().height;

    if(position) {
        var newX = tX;
        var newY = tY;
        switch(position) {
            case TOP:
                newY = line.getBBox().y - (tH/2) - 5;
            break;
            case RIGHT:
                newX = newX + tW/2 + 5;
            break;
            case BOTTOM:
                newY = line.getBBox().y + line.getBBox().height + 5;
            break;
            case LEFT:
                newX = line.getBBox().x - (tW/2) - 5;
            break;
        }
        lineLabel.attr({'x': newX, 'y': newY});
    }
    return line;
}

/*
    XXX Only draws connected links where the main object is on the left and
    the objects to connect are in a column to the right (e.g. ReportingSystem).
    First connected object is in line with main object, others are below this.
*/
function addConnectedLinks(baseObj, linkObjs, linkLabel) {
    // Arrow from first Report to ReportingSystem
    addLink(reports[0], baseObj, linkLabel, TOP);
    // Lines from remaining Reports to ReportingSystem
    if(reports.length > 1) {
        bb1 = baseObj.getBBox();
        x1 = bb1.x + bb1.width;
        y1 = bb1.y + (bb1.height/2);
        xMid = x1 + ((reports[0].getBBox().x - x1) /2);
        for(i = 1; i < reports.length; i++) {
            bb2 = reports[i].getBBox();
            x2 = bb2.x;
            y2 = bb2.y + (bb2.height/2);
            var pStr = "M " + x2 + "," + y2 + " L " + xMid + "," + y2 + " L " + xMid + "," + y1
            var l = paper.path(pStr);
            l.attr({stroke: l, "stroke-width": 3, fill: "none"})
        }
    }
}


function addTextLabel(x, y, width, text, uri, fontSize, fontWeight, maxLines, colour) {
	var tLabel = paper.text(x, y, text);
	tLabel.attr({"font-size": fontSize, fill: colour, cursor: "default"});
	if(fontWeight != null && fontWeight != "")
	    tLabel.attr({"font-weight": fontWeight});
	if(uri != null && uri != "")
		tLabel.attr({href: uri, cursor: "pointer"});
	textWrap(tLabel, width, maxLines);
}


function textWrap(t, width, maxLines) {
	var content = t.attr("text");
	var abc = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
	t.attr({
		'text-anchor' : 'center',
		"text" : abc
	});
	var letterWidth = t.getBBox().width / abc.length;

	t.attr({
		"text" : content
	});
	var words = content.split(" ");
	var x = 0, y = 0, s = [], lines = 0;
	for ( var i = 0; i < words.length; i++) {
		var l = words[i].length;
		// String is too big for remaining line
		if (x + (l * letterWidth) > width) {
		    // String is too big for an entire line
		    if((l * letterWidth) > width) {
		        maxL = Math.floor((width-x)/letterWidth) - 1;
		        word1 = words[i].slice(0, maxL);
		        // If not last line, add a "-"
		        if(lines != maxLines - 1)
		            word1 += "-\n";
		        // Last line, so add "..."
		        else
		            word1 += "...";
		        word2 = words[i].slice(maxL, words[i].length);
		        s.push(word1);
		        words.splice(i, 1, word2);
		        x = 0;
		        lines++;
		        if(lines == maxLines)
		            break;
		        i--;
		        continue;
		    }
            if(lines != maxLines - 1)
			    s.push("\n");
			else if(lines == maxLines - 1) {
			    if(x + (l*letterWidth) > width - 3)
			        s.pop();
				if (i != words.length - 1)
					s.push("...");
				break;
			}
			x = 0;
			lines++;
		}
		x += l * letterWidth;
		s.push(words[i] + " ");
	}
	t.attr({
		"text" : s.join("")
	});
}
