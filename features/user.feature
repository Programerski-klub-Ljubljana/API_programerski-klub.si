Feature: Sign in
  In order to get new club members,
  I want sign in form on which outside person,
  can apply for club membership.

  Scenario: Normal usage
    Given that outside person wants to sign in
    And he enters his personal info in the form
    And he enters his contact informations in the form
    When he submits the form
    Then he becomes club member
    Then he should get verification messages

Feature: Verification message
  In order for new club member to verify contact informations,
  he will get verification messages on which he can confirm
  contact ownership.

  Scenario: Normal usage
    Given that person gets verification message
    When he confirms verification message
    Then confirmed contact will be used for club activities
