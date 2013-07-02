$(document).ready(function (event) {

    customizedInput = false;

    $('#addModal').on('shown', function (e) {
        if (!customizedInput) {
            customizedInput = true;
            $('[type=file]').customFileInput();
            }
    });

    $('#editModal').on('shown', function (e) {
        if (!customizedInput) {
            customizedInput = true;
            $('[type=file]').customFileInput();
            }
    });

    $('.portaltype-plone-site a[data-toggle="tab"]').on('show', function (e) {
        targetid = $(this).data('target');
        remote = $(targetid).data('remote');
        if (remote) {
            $(targetid).load(portal_url + "/" + remote, function (event) {
                // Favorites
                $('#communitylist').on('click', '.favorite', function(event) {
                  event.preventDefault();
                  var community_url = $(this).data()['community'];
                  $.get(community_url + '/toggle-favorite');
                  if ($('i', this).hasClass('fa-icon-star')) {
                    $('i', this).addClass('fa-icon-star-empty').removeClass('fa-icon-star');
                  } else {
                    $('i', this).addClass('fa-icon-star').removeClass('fa-icon-star-empty');
                  }
                });
                $('.sortablelist').mixitup({layoutMode: 'list'});
            });
        }
        $('#menusup .active').removeClass('active');
        $(e.target.parentElement.parentElement).addClass('active');
    });

    $(function(){

        var $username = $("#box_perfil #user h2");

        var $letters = $username.text().length;

        if (($letters >= 1) && ($letters < 10)) {
            $username.css("font-size", "20px");
        }
        else if (($letters >= 10) && ($letters < 20)) {
            $username.css("font-size", "20px");
        }
        else if (($letters >= 20) && ($letters < 30)) {
            $username.css("font-size", "16px");
        }
        else if (($letters >= 30) && ($letters < 40)) {
            $username.css("font-size", "14px");
        }
        else {
            $username.css("font-size", "20px");
        }

    });

    // Favorites for search communities form
    $('#communitylist').on('click', '.favorite', function(event) {
      event.preventDefault();
      var community_url = $(this).data()['community'];
      $.get(community_url + '/toggle-favorite');
      if ($('i', this).hasClass('fa-icon-star')) {
        $('i', this).addClass('fa-icon-star-empty').removeClass('fa-icon-star');
      } else {
        $('i', this).addClass('fa-icon-star').removeClass('fa-icon-star-empty');
      }
    });

    // Community search
    $('.searchInput').on('keyup', function(event) {
        var query = $(this).val();
        $('.listingBar').hide();
        $.get(portal_url + '/search-communities-ajax', { q: query }, function(data) {
            $('#communitylist').html(data);
        });
    });

    // # of thinnkinns updater
    $(window).on('maxui-posted-activity', function(event) {
        int_activities = parseInt($('.currentactivity').text(), 10);
        $('.currentactivity').text(int_activities + 1);
    });

    // Dialog search communities
    $('#communitylist').on('click', '.delete', function(event) {
        event.preventDefault();
        var $this = $(this);
        alertify.confirm("Si cliqueu aquí, esborrareu la comunitat " + $this.data()['name'], function (e) {
            if (e) {
                // user clicked "ok"
                url = $this.attr('href');
                $.ajax({
                    type: "POST",
                    url: url,
                    data: {
                    'form.submitted': '1',
                    '_authenticator': $this.data()['authenticator']
                    },
                    error: function() {
                        alertify.error("Error when removing community");
                    },
                    success: function() {
                        $this.parent().parent().parent().remove();
                        alertify.success("Successfully removed");
                        console.log("ok");
                    }
                });
            } else {
                // user clicked "cancel"
            }
        });
    });

    $('#communitylist').on('click', '.subscribe', function(event) {
        event.preventDefault();
        var $this = $(this);
        alertify.confirm("Voleu subscrivir-vos a la comunitat " + $this.data()['name'] + "?", function (e) {
            if (e) {
                // user clicked "ok"
                community_url = $this.data()['community'];
                $.ajax({
                    type: "GET",
                    url: community_url + "/toggle-subscribe",
                    error: function() {
                        alertify.error("Error when (un)subscribing to the community");
                    },
                    success: function() {
                        if ($('i', $this).hasClass('fa-icon-check')) {
                            $('i', $this).addClass('fa-icon-check-empty').removeClass('fa-icon-check');
                            alertify.success("Successfully unsubscribed");
                        } else {
                            $('i', $this).addClass('fa-icon-check').removeClass('fa-icon-check-empty');
                            alertify.success("Successfully subscribed");
                        }
                        console.log("ok");
                    }
                });
            } else {
                // user clicked "cancel"
            }
        });
    });

});
