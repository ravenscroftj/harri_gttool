(function() {
  'use strict';

  angular
    .module('app.news.article', [])
    .constant('defaultTitle', 'News Article Matcher')
    .controller('ArticleController', ArticleController);

  /* @ngInject */
  function ArticleController($scope, $state, $sce, defaultTitle, newsService) {
    var articleVm = this;

    articleVm.title = defaultTitle;

    articleVm.articleID = $state.params.articleID;

    articleVm.loadFromState = loadFromState;

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      articleVm.loadFromState();
    });

    $scope.highlight = function(text, search) {
      if (!search) {
          return $sce.trustAsHtml(text);
      }
      return $sce.trustAsHtml(text.replace(new RegExp(search, 'gi'), '<span class="highlightedText">$&</span>'));
    };

    $scope.getPeople = function() {
      newsService.getPeople(articleVm.articleID).then(function(data){
        $scope.people=data;
      });
    };

    $scope.getInstitutions = function(){
      newsService.getInstitutions(articleVm.articleID).then(function(data){
        console.log("Institutions");
        $scope.insts=data;
      });
    };



    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      newsService.getArticle(articleVm.articleID).then(function(data){
        console.log(data);
        data.content = data.content.replace(/\n/g,"<br>");
        $scope.article = data
      });

    }
  }

})();
