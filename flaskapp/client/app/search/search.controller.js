(function() {
  'use strict';

  angular
    .module('app.search', [])
    .constant('defaultTitle', 'An elegant title...')
    .controller('SearchController', SearchController);

  /* @ngInject */
  function SearchController($scope, $state, defaultTitle, searchService) {
    var newsVm = this;

    newsVm.title = defaultTitle;
    newsVm.searchTerm = null;
    newsVm.selected = {};
    newsVm.searchResults = [];

    newsVm.loadFromState = loadFromState;
    newsVm.search = search;

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      newsVm.loadFromState();
    });

    // Load local variables from the state (the URL of the page).
    function loadFromState() {
      newsVm.searchTerm = $state.params.term;
      if (newsVm.searchTerm) {
        searchService.search({
          'term': newsVm.searchTerm
        }).then(function (data) {
          newsVm.searchResults = data;
        });
      }
    }

    function search() {
      $state.go('search.term', {
        term: newsVm.searchTerm
      });
    }
  }

})();
