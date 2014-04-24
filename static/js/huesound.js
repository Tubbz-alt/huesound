function init() 
{
    coverHack.init("US");
}

mbalbums = function(data) 
{
    coverHack.processCovers(data);
};

coverHack = {
    allColors: ['#000000', '#CC3333', '#FF3333', '#FF6633', '#FF9933', '#FFCC66', '#FFFF33', '#CCCC33', '#99CC33', '#33CC33', '#009933', '#006633', '#33CC99', '#33CCFF', '#3366CC', '#333399', '#000066', '#663399', '#990099', '#990066', '#FF0066', '#CCCC99', '#996666', '#996633', '#663333', '#CC9966', '#996633', '#663300', '#333300', '#330000', '#333333', '#666666'],
    // 30 gives us a 6x5 grid, looks nice
    albumCount: 30,
    lastColor:"",
    lastOffset : 0,
    firstRun: true,
    processing: false,
    local: false,
    imgUrlBase: "",
    data: null,
    albumClicked : false,
    r_page: null,
    pie : null,
    colorWheelOffsetY : 0,
    colorWheelOffsetX : 0,
    colorWheelDia : 0,
    playerStart : '<iframe src="https://embed.spotify.com/?uri=',
    playerEnd : '" width="300" height="380" frameborder="0" allowtransparency="true"></iframe>',
    fetchCovers: function(color, offset) {
            console.log("color: " + color);
            if (offset < 0)
                offset = 0;
            coverHack.lastColor = color;
            coverHack.lastOffset = offset;
            if(coverHack.firstRun) {
                    $( "#instructions_txt" ).toggle( 'puff', {}, 500, function() {
                            $( "#albumsContainer" ).show();
                    } );
                    coverHack.firstRun = false;
            } else if(!coverHack.processing) {
                    coverHack.view.hideAlbums();
            } else {
                    return;
            }
            coverHack.view.changeBG(color);
            color = color.replace('#', '');
            coverHack.processing = true;
            url = "/%color%/" + coverHack.albumCount + "/" + coverHack.country + "/j/%offset%";
            url = url.replace(/%color%/, color),
            url = url.replace(/%offset%/, offset),
            console.log(url);
            $.ajax({
                    url: url, 
                    timeout: 5000,
                    dataType: "jsonp",
                    jsonp: false,
                    jsonpCallback: "mbalbums",
                    cache: false,
                    error : function () { console.log("Ajax error"); }

            });
    },
    processCovers: function(data) {
            var tracks = [], i, j = 0;

            coverHack.processing = false;
            coverHack.data = data;
            coverHack.view.showAlbums();

            for(i = 0; i < coverHack.data.length; i++) 
                coverHack.view.showPlay(i);
    },
    util: {
            // http://stackoverflow.com/questions/1507931/generate-lighter-darker-color-in-css-using-javascript
            color: {
                    pad: function(num, totalChars) {
                        var pad = '0';
                        num = num + '';
                        while (num.length < totalChars) {
                            num = pad + num;
                        }
                        return num;
                    },

                    // Ratio is between 0 and 1
                    changeColor: function(color, ratio, darker) {
                        // Trim trailing/leading whitespace
                        color = color.replace(/^\s*|\s*$/, '');

                        // Expand three-digit hex
                        color = color.replace(
                            /^#?([a-f0-9])([a-f0-9])([a-f0-9])$/i,
                            '#$1$1$2$2$3$3'
                        );

                        // Calculate ratio
                        var difference = Math.round(ratio * 256) * (darker ? -1 : 1),
                            // Determine if input is RGB(A)
                            rgb = color.match(new RegExp('^rgba?\\(\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '\\s*,\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '\\s*,\\s*' +
                                '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
                                '(?:\\s*,\\s*' +
                                '(0|1|0?\\.\\d+))?' +
                                '\\s*\\)$', 'i')),
                            alpha = !!rgb && rgb[4] !== null ? rgb[4] : null,

                            // Convert hex to decimal
                            decimal = !!rgb? [rgb[1], rgb[2], rgb[3]] : color.replace(
                                /^#?([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])/i,
                                function() {
                                    return parseInt(arguments[1], 16) + ',' +
                                        parseInt(arguments[2], 16) + ',' +
                                        parseInt(arguments[3], 16);
                                }
                            ).split(/,/),
                            returnValue;

                        // Return RGB(A)
                        return !!rgb ?
                            'rgb' + (alpha !== null ? 'a' : '') + '(' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[0], 10) + difference, darker ? 0 : 255
                                ) + ', ' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[1], 10) + difference, darker ? 0 : 255
                                ) + ', ' +
                                Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[2], 10) + difference, darker ? 0 : 255
                                ) +
                                (alpha !== null ? ', ' + alpha : '') +
                                ')' :
                            // Return hex
                            [
                                '#',
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[0], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2),
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[1], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2),
                                coverHack.util.color.pad(Math[darker ? 'max' : 'min'](
                                    parseInt(decimal[2], 10) + difference, darker ? 0 : 255
                                ).toString(16), 2)
                            ].join('');
                    },
                    lighterColor: function(color, ratio) {
                        return coverHack.util.color.changeColor(color, ratio, false);
                    },
                    darkerColor: function(color, ratio) {
                        return coverHack.util.color.changeColor(color, ratio, true);
                    }
            }
    },
    view: {
            imageSize :function() {
                    console.log("screen w: " + $(window).width() + " screen h: " + $(window).height() + "col " + $("#left-column").width());
                    w = $(window).width() - $("#left-column").width();
                    h = $(window).height();
                    if (w < h)
                        size = Math.floor((w - (10 * 6) - 15) / 6);
                    else
                        size = Math.floor((h - (10 * 5) - 15) / 5);
                    console.log("max w: " + w + " max h: " + h + " album s: " + size);
                    return size;
            },
            setContainerSize: function(image_size) {
                    w = ((image_size + 10) * 6) + 15;
                    max_w = $(window).width() - $("#left-column").width();
                    if (w > max_w) w = max_w;
                    $("#albumsContainer").width(w);

                    h = ((image_size + 10) * 5) + 15;
                    max_h = $(window).height();
                    if (h > max_h) h = max_h;
                    $("#albumsContainer").height(h);
                    console.log("w: " + w + " h: " + h);
            },
            albumTpl: '<li id="%i%">' 
                     +'  <img src="http://o.scdn.co/300/%image_id%" id="img%i%" class="grow"' 
                     +'       style="width: %size%px; height: %size%px;" onclick="coverHack.album_clicked(%i%)">'
                     +'</li>',
            showAlbums: function() {
                    $("#progress" ).hide();

                    var i,
                            album,
                            tpl,
                            albumsHTML = [];
                    album_size = coverHack.view.imageSize();
                    coverHack.view.setContainerSize(album_size);
                    for(i = 0; i < coverHack.data.length; i++) {
                            album = coverHack.data[i];
                            tpl = coverHack.view.albumTpl;
                            tpl = tpl.replace(/%image_id%/g, album.image_id);
                            tpl = tpl.replace(/%i%/g, i);
                            tpl = tpl.replace(/%size%/g, album_size);
                            tpl = tpl.replace(/%id%/g, album.album_uri);
                            albumsHTML.push(tpl);
                    }
                    // insert albums into page
                    $('#albums').html(albumsHTML.join(''));
            },
            hideAlbums: function() {
                    $("#progress").show();
                    // loop through albums and hide them all, one after another
                    $('#albums li').each( function(i, album) {
                            $(album).remove();
                    });
            },
            changeBG: function(color) {
                    color = coverHack.util.color.lighterColor(color, 0.6);
                    $('body').animate( { backgroundColor: color }, 1000);
            },
            showPlay: function(albumIndex) {
                    var albumCover = $('#albums #' + albumIndex);
                    albumCover.data('album_uri', coverHack.data[albumIndex].album_uri);
                    albumCover.addClass('play');
                    albumCover.append('<div class="playbtn"></div>');
                    $('.playbtn', albumCover).fadeIn(500);
            },
            resize: function() {
                    album_size = coverHack.view.imageSize();
                    for(i = 0; i < coverHack.albumCount; i++) {
                        $("#img" + i).css("width", album_size);
                        $("#img" + i).css("height", album_size);
                    }
                    coverHack.view.setContainerSize(album_size);
                    coverHack.view.createColorWheel();
            },
            calculateColorWheelDims: function () {
                    var w = $("#color-wheel").width();
                    var h = $("#color-wheel").height();
                    var margin = 30;
                    coverHack.colorWheelDia = w / 2 - margin;
                    coverHack.colorWheelOffsetY = coverHack.colorWheelDia + (margin / 2);
                    coverHack.colorWheelOffsetX = coverHack.colorWheelDia + margin;
            },
            createColorWheel: function() {
                    coverHack.view.calculateColorWheelDims();
                    if (coverHack.pie) {
                        delete(coverHack.pie);
                        delete(coverHack.r_page);
                        coverHack.pie = null;
                        coverHack.r_page = null;
                    }

                    coverHack.r_page = Raphael("color-wheel");
                    pie = coverHack.r_page.piechart(coverHack.colorWheelOffsetX, 
                                                    coverHack.colorWheelOffsetY, 
                                                    coverHack.colorWheelDia, 
                                                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 
                                                    {colors: coverHack.allColors});
                    pie.hover(function () {
                            this.sector.stop();
                            this.sector.scale(1.1, 1.1, this.cx, this.cy);
                    }, function () {
                            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");
                    });
                    pie.click(function() {
                            offset = 0;
                            coverHack.fetchCovers(this.sector.attrs.fill, 0);
                    });
                    coverHack.pie = pie;
            }
    },
    album_clicked: function(index) {
        album_uri = coverHack.data[index].album_uri;
        //coverHack.albumClicked = true;
        $("#player").html(coverHack.playerStart + album_uri + coverHack.playerEnd);
    },
    next_page: function() {
        coverHack.fetchCovers(coverHack.lastColor, coverHack.lastOffset + coverHack.albumCount);
    },
    prev_page: function() {
        coverHack.fetchCovers(coverHack.lastColor, coverHack.lastOffset - coverHack.albumCount);
    },
    init: function(country) {
            coverHack.country = country;
            $(window).resize(coverHack.view.resize);
            coverHack.view.resize();
            /* $('.play', $('#albums')).live("click", function(e) {
                if (!coverHack.albumClicked)
                    coverHack.play_clicked($(this).data('album_uri'));
                coverHack.albumClicked = false;
            }); */
            $('#play').attr("src", "");
    }
};
