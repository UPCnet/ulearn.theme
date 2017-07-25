  $(document).ready(function (event) {
      intervalflash = setInterval(function (event) {
          $('.ulearnboxflash .carousel').carousel('cycle');
          clearInterval(intervalflash);
      }, 2000);
  })
