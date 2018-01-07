(function() {
  'use strict';

  angular
    .module('app.news.article', [])
    .constant('defaultTitle', 'News Article Matcher')
    .controller('ArticleController', ArticleController);

  /* @ngInject */
  function ArticleController($scope, $state, defaultTitle, newsService) {
    var articleVm = this;

    articleVm.title = defaultTitle;


    articleVm.loadFromState = loadFromState;

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      articleVm.loadFromState();
    });

    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      newsService.getArticle($state.params.articleID).then(function(data){
        console.log(data);
        data.content = data.content.replace(/\n/g,"<br>");
        $scope.article = data
      });

    }
  }

})();
