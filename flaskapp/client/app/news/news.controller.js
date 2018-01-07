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
    newsVm.searchTerm = null;
    newsVm.selected = {};
    newsVm.searchResults = [];

    newsVm.loadFromState = loadFromState;
    newsVm.search = search;

    $scope.newsClick = function(articleID){
      $state.go('news.article', {
        articleID: articleID
      });
    }

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      newsVm.loadFromState();
    });

    // Load local variables from the state (the URL of the page).
    function loadFromState() {
      $scope.isLoading = true;
      newsService.getNews().then(function(data){
        $scope.isLoading = false;
        newsVm.newsArticles = data
      });

    }

    function search() {
      $state.go('search.term', {
        term: newsVm.searchTerm
      });
    }
  }

})();
