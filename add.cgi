#!/usr/bin/perl
use strict;

use lib qw[/home/httpd/html/www/markup/html/whatpm
           /home/wakaba/work/manakai2/lib];

use CGI::Carp qw[fatalsToBrowser];
require Message::CGI::Carp;

require 'users.pl';

require Message::CGI::HTTP;
require Encode;
my $cgi = Message::CGI::HTTP->new;
$cgi->{decoder}->{'#default'} = sub {
  return Encode::decode ('utf-8', $_[1]);
};

require Message::DOM::DOMImplementation;
my $dom = Message::DOM::DOMImplementation->new;

my $path = $cgi->path_info;
$path = '' unless defined $path;

my @path = split m#/#, percent_decode ($path), -1;
shift @path;

if (@path == 1 and $path[0] eq 'new-user') {
  if ($cgi->request_method eq 'POST') {
    lock_start ();
    binmode STDOUT, ':encoding(utf-8)';
    
    my $user_id = $cgi->get_parameter ('user-id');

    if ($user_id !~ /\A[0-9a-z-]{4,20}\z/) {
      print_error (400, qq[User id "$user_id" is invalid; use characters [0-9a-z-]{4,20}]);
      exit;
    }
    
    if (get_user_prop ($user_id)) {
      print_error (400, qq[User id "$user_id" is already used]);
      exit;
    }

    my $pass_crypted = check_password ($cgi);

    my $user_prop = {id => $user_id, pass_crypted => $pass_crypted};
    set_user_prop ($user_id, $user_prop);

    regenerate_htpasswd_and_htgroup ();
    commit ();

    my $user_url = get_absolute_url ('../edit/users/' . $user_id . '/');

    print qq[Status: 201 User registered
Location: $user_url
Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>User "@{[htescape ($user_id)]}" registered</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>User "@{[htescape ($user_id)]}" registered</h1>
<p>Your user account is created successfully.
<p>See <a href="@{[htescape ($user_url)]}">your user account information page</a>.];
    exit;
  } else {
    binmode STDOUT, ":encoding(utf-8)";
    print qq[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>Create a new user account</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>Create a new user account</h1>

<form action=new-user accept-charset=utf-8 method=post>

<p><strong>User id</strong>: <input type=text name=user-id
maxlength=20 size=10 required pattern="[0-9a-z-]{4,20}"
title="Use a string of characters 'a'..'z', '0'..'9', and '-' with length 4..10 (inclusive)">

<p><strong>Password</strong>: <input type=password name=user-pass
size=10 required pattern=".{4,}" title="Type 4 characters at minimum">

<p><strong>Password</strong> (type again): <input type=password
name=user-pass2 size=10 required pattern=".{4,}">

<p><input type=submit value=Create>

</form>];
    exit;
  }
} elsif (@path == 0) {
  my $root_url = get_absolute_url ('add/new-user');

  print qq[Status: 301 Moved permanently
Location: $root_url
Content-Type: text/html; charset=us-ascii

See <a href="@{[htescape ($root_url)]}">other page</a>.];
  exit;
}

print_error (404, 'Not found');
exit;

sub percent_decode ($) {
  return $dom->create_uri_reference ($_[0])
      ->get_iri_reference
      ->uri_reference;
} # percent_decode

sub get_absolute_url ($) {
  return $dom->create_uri_reference ($_[0])
      ->get_absolute_reference ($cgi->request_uri)
      ->get_iri_reference 
      ->uri_reference;
} # get_absolute_url
