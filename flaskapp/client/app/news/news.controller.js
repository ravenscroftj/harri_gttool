(function() {
  'use strict';

  angular
    .module('app.news', [])
    .constant('defaultTitle', 'List News Articles')
    .controller('NewsController', NewsController);

  /* @ngInject */
  function NewsController($scope, $state, defaultTitle, newsService) {
    var newsVm = this;

    newsVm.title = defaultTitle;
    newsVm.searchTerm = null;
    newsVm.selected = {};
    newsVm.searchResults = [];

    newsVm.loadFromState = loadFromState;
    newsVm.search = search;

    $scope.newsClick = function(articleID){
      alert("Article " + articleID)
      $state.go('.article', {
        articleID: articleID
      });
    }

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      newsVm.loadFromState();
    });

    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      newsService.getNews().then(function(data){
        console.log(data);
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
