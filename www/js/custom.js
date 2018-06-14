$(document).ready(function () {

    'use strict';

    var locations = $('.location');
    var domainSlider = $('.pricing-2 .owl-carousel');
    var testimonialsSlider = $('.testimonials-2 .owl-carousel');

    if(locations.length) {
        locations.tooltip({
            template: '<div class="tooltip tooltip-location" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
        });
    }

    if(domainSlider.length) {
        domainSlider.owlCarousel({
            items: 4,
            margin: 15,
            autoplay: true,
            loop: true,
            dots: true,
            mouseDrag: false,
            responsive : {
                0: {
                    items: 1
                },
                480: {
                    items: 2
                },
                992: {
                    items: 4
                }
            }
        });
    }

    if(testimonialsSlider.length) {
        testimonialsSlider.owlCarousel({
            items: 1,
            autoplay: true,
            loop: true,
            mouseDrag: false,
            dots: true
        });
    }

    $('.testimonials-card__next-button').on('click', function(){
        testimonialsSlider.trigger('next.owl.carousel');
    });

    $('.testimonials-card__prev-button').on('click', function(){
        testimonialsSlider.trigger('prev.owl.carousel');
    });

    $('main .navbar li a[href*="#"]').not('[href="#"]').not('[href="#0"]').on('click', function(event) {
            if (
                location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '')
                &&
                location.hostname === this.hostname
            ) {
                // Figure out element to scroll to
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                // Does a scroll target exist?
                if (target.length) {
                    // Only prevent default if animation is actually gonna happen
                    event.preventDefault();
                    $('html, body').animate({
                        scrollTop: document.querySelector(this.hash).offsetTop - 72
                    }, 1000);
                }
            }
        });

    var options =  {
        layout: {
            padding: {
                top: 20
            }
        },
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display:false
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#edf0f2"
                },
                ticks: {
                    beginAtZero:true,
                    callback: function(value) {
                        return value + '.00';
                    }
                },
                afterFit: function(scaleInstance) {
                    scaleInstance.width = 65; // sets the width to 65px
                }
            }]
        },
        events: false,
        tooltips: {
            enabled: false
        },
        hover: {
            animationDuration: 0
        },
        animation: {
            duration: 1,
            onComplete: function () {
                var chartInstance = this.chart,
                    ctx = chartInstance.ctx;
                ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.names[index];
                        ctx.fillText(data, bar._model.x, bar._model.y - 5);
                    });
                });
            }
        }
    };

    var options2 = {
        layout: {
            padding: {
                top: 20
            }
        },
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display:false
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "#edf0f2"
                },
                ticks: {
                    beginAtZero:true,
                    callback: function(value) {
                        return value + ' MB/s';
                    }
                },
                afterFit: function(scaleInstance) {
                    scaleInstance.width = 65; // sets the width to 65px;
                }
            }]
        },
        events: false,
        tooltips: {
            enabled: false
        },
        hover: {
            animationDuration: 0
        },
        animation: {
            duration: 1,
            onComplete: function () {
                var chartInstance = this.chart,
                    ctx = chartInstance.ctx;
                ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.names[index];
                        ctx.fillText(data, bar._model.x, bar._model.y - 5);
                    });
                });
            }
        }
    };

    var ctx = document.getElementById("myChart");

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ["768MB", "1GB", "C3 Large"],
            datasets: [{
                label: '# of Votes',
                data: [1500, 1250, 750],
                names: ['Austin', 'DataScience', 'AWS'],
                backgroundColor: [
                    '#00b4ff',
                    '#e6e9eb',
                    '#e6e9eb'
                ]
            }]
        },
        options: options
    });

    var ctx2 = document.getElementById("myChart2");
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ["768MB", "1GB", "C3 Large"],
            datasets: [{
                label: '# of Votes',
                data: [300, 75, 25],
                names: ['Austin', 'DataScience', 'AWS'],
                backgroundColor: [
                    '#00b4ff',
                    '#e6e9eb',
                    '#e6e9eb'
                ]
            }]
        },
        options: options
    });

    var ctx3 = document.getElementById("myChart3");
    new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: ["768MB", "1GB", "C3 Large"],
            datasets: [{
                label: '# of Votes',
                data: ['450', '160', '100'],
                names: ['Austin', 'DataScience', 'AWS'],
                backgroundColor: [
                    '#00b4ff',
                    '#e6e9eb',
                    '#e6e9eb'
                ]
            }]
        },
        options: options2
    });
});

$(document).scroll(function() {

    var navbar = $('.navbar');
    var modal = $('#newsletterModal');

    if ($(document).scrollTop() >= 250) {
        navbar.addClass('top-fixed');
    }else {
        navbar.removeClass('top-fixed');
    }

    if ($(document).scrollTop() >= 1600) {

        if (!localStorage.getItem("done")) {
            setTimeout(function() {
                modal.modal('show');
            }, 1400);
        }
        localStorage.setItem("done", true);
    }

});