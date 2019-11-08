<head>
    <meta charset="UTF-8">
    <title> Not all bugs are the same/title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="stylesheets/normalize.css" media="screen">
    <link href='https://fonts.googleapis.com/css?family=Open+Sans:400,700' rel='stylesheet' type='text/css'>
    <link rel="stylesheet" type="text/css" href="stylesheets/stylesheet.css" media="screen">
    <link rel="stylesheet" type="text/css" href="stylesheets/github-light.css" media="screen">
 </head>



## Replication Package

Not all bugs are the same: Analyzing differences between bugs, and the ability of traditional independent variables to predict modern bug metrics.

Kilby James Baron (1), Harold Valdivia-Garcia (2), Gema Rodriguez-Perez (1), Meiyappan Nagappan (1), and Michael Godfrey (1)

(1) Department of Software Engineering, University of Waterloo, Waterloo, Ontario  
(2) Bloomberg LP, United States


<a href="https://github.com/uw-swag/Not-All-Bugs-Are-The-Same" class="btn">View on GitHub</a>
<a href="https://github.com/uw-swag/Not-All-Bugs-Are-The-Same/archive/master.zip" class="btn">Download .zip</a>
<a href="https://github.com/uw-swag/Not-All-Bugs-Are-The-Same//tarball/master" class="btn">Download .tar.gz</a>

---

## Abstract

To prioritize bug-prone software entities, many previous studies use the number of bugs as dependent variable. Such a dependent variable assumes that "all bugs are the same". However, this assumption may not hold because bugs have different origin, impact or even cost. In fact, the dependent variable might differ depending practitioners' needs. For instance, industrial customers might prefer to prioritize bug-prone software entities based on their cost to fix rather than the number of bugs.

To study whether (1) all bugs are the same, and (2) the choice of dependent variable affects the prioritization of bug-prone software entities, we analyzed 33,000 bugs from 11 software projects trough a quantitative and qualitative large-scale study. Specifically, we used three dependent variables bug-fixed size, developer experience, and bug's priority to understand (1) the difference of bugs based on these metrics, and (2) the impact on prioritization and prediction models when using these variables instead of number of bugs.

Our results shows that (1) the assumption "all bugs are the same" does not hold since different bugs are fixed by developers with different levels of experience; (2) the prioritization of files is considerably different when we use different dependent variables; and (3) when the dependent variable changes, the relative importance of the independent variables remain the same, but the variability explained in the model drops considerably. Thus, we find evidence that the choice of dependent variable greatly affects the prediction model.

---



### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
