#!/usr/bin/perl
use strict;

use lib qw[/home/httpd/html/www/markup/html/whatpm
           /home/wakaba/work/manakai2/lib];

use CGI::Carp qw[fatalsToBrowser];
require Message::CGI::Carp;

require 'users.pl';
require 'texts.pl';

require Message::CGI::HTTP;
require Encode;
my $cgi = Message::CGI::HTTP->new;
$cgi->{decoder}->{'#default'} = sub {
  return Encode::decode ('utf-8', $_[1]);
};

our $Lang = 'ja'
    if $cgi->get_meta_variable ('HTTP_ACCEPT_LANGUAGE') =~ /\bja\b/; ## TODO: ...

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
      print_error (400,
                   q[User id %s is invalid; use characters [0-9a-z-]{4,20}],
                   $user_id);
      exit;
    }
    
    if (get_user_prop ($user_id)) {
      print_error (400, q[User id %s is already used], $user_id);
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
<title>];
    print_text ('User %s registered', sub { print '', htescape ($user_id) });
    print q[</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>];
    print_text ('User %s registered', sub { print '', htescape ($user_id) });
    print q[</h1><p>];
    print_text ('Your user account is created successfully.');
    print q[<p>];
    print_text ('See %s.', sub {
      print q[<a href="@{[htescape ($user_url)]}">];
      print_text ('your user account information page');
      print q[</a>];
    });
    exit;
  } else {
    binmode STDOUT, ":encoding(utf-8)";
    print q[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>];
    print_text ('Create a new user account');
    print q[</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>];
    print_text ('Create a new user account');
    print q[</h1>

<form action=new-user accept-charset=utf-8 method=post>

<p><strong>];
    print_text ('User id');
    print q[</strong>: <input type=text name=user-id
maxlength=20 size=10 required pattern="[0-9a-z-]{4,20}"> (];
    print_text ('Use [0-9a-z-]{4,20}.');
    print q[)<p><strong>];
    print_text ('Password');
    print q[</strong>: <input type=password name=user-pass
size=10 required pattern=".{4,}"> (];
    print_text ('Type 4 characters at minimum');
    print q[)<p><strong>];
    print_text ('Password');
    print q[</strong> (];
    print_text ('type again');
    print q[): <input type=password
name=user-pass2 size=10 required pattern=".{4,}">

<p><input type=submit value="];
    print_text ('Create');
    print q["></form>];
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
