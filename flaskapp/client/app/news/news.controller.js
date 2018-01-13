(function() {
  'use strict';

  angular
    .module('app.news', [])
    .constant('defaultTitle', 'List News Articles')
    .controller('NewsController', NewsController);

  /* @ngInject */
  function NewsController($scope, $state, defaultTitle, newsService) {
    var newsVm = this;
    $scope.$state = $state;

    newsVm.title = defaultTitle;
    newsVm.selected = {};

    newsVm.loadFromState = loadFromState;

    $scope.newsClick = function(articleID){
      $state.go('news.article', {
        articleID: articleID
      });
    }

    $scope.nextPage = function(){
      $state.go('.', {
        page: parseInt($state.params.page)+1
      });
    }


    $scope.previousPage = function(){
      console.log("HOHGOH")
      $state.go('.', {
        page: parseInt($state.params.page)-1
      });
    }



    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      newsVm.loadFromState();
    });

    // Load local variables from the state (the URL of the page).
    function loadFromState() {
      $scope.hidden = $state.current.name == "news.hidden";
      $scope.linked = $state.current.name == "news.linked";

      $scope.isLoading = true;

      var offset = ($state.params.page-1) * 10;

      newsService.getNews($scope.hidden, $scope.linked, offset).then(function(data){
        $scope.isLoading = false;
        newsVm.newsArticles = data
      });

    }

  }

})();
