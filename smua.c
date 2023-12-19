/*
 *  @(!--#) @(#) suma.c, version 004, 30-may-2020
 *
 *  a (S)imple (U)ser (M)ail (A)gent for receiving email
 *  through the .forward mechanism and placing each
 *  email into a separate file in $HOME/.suma
 *
 */

/****************************************************************/

/*
 *  includes
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <syslog.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

/****************************************************************/

/*
 *  defines
 */

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define BUFFER_SIZE 24

#define MAX_LINE_LENGTH 8192

#define SMUA_SUBDIR ".smua"

/****************************************************************/

/*
 *  Main
 */

int main(argc, argv)
  int   argc;
  char *argv[];
{
  int                debug;
  int                priority;
  char              *home;
  char               smuasubdir[MAX_LINE_LENGTH + sizeof(char)];
  char               msgfilename[MAX_LINE_LENGTH + sizeof(char)];
  char               lockfilename[MAX_LINE_LENGTH + sizeof(char)];
  struct timeval     tv;
  struct timezone    tz;
  int                msgfd;
  int                stdinfd;
  int                lockfd;
  unsigned char      buf[BUFFER_SIZE];
  int                n;

  if (getenv("DEBUG") == NULL) {
    debug = FALSE;
  } else {
    debug = TRUE;
  }

  priority = LOG_USER | LOG_ERR;

  openlog(NULL, LOG_NDELAY | LOG_PID, LOG_USER);

  if (debug) {
    syslog(priority, "program %s starting", argv[0]);
  }

  home = getenv("HOME");

  if (home == NULL) {
    syslog(priority, "cannot determine value of HOME environment variable");
    return 1;
  }

  strncpy(smuasubdir, home,        MAX_LINE_LENGTH - sizeof(char));
  strncat(smuasubdir, "/",         MAX_LINE_LENGTH - sizeof(char));
  strncat(smuasubdir, SMUA_SUBDIR, MAX_LINE_LENGTH - sizeof(char));

  if (debug) {
    syslog(priority, "SMUA subdirectory is \"%s\"", smuasubdir);
  }

  if (chdir(smuasubdir) != 0) {
    syslog(priority, "cannot change directory to \"%s\"", smuasubdir);
    return 1;
  }

  if (gettimeofday(&tv, &tz) != 0) {
    syslog(priority, "cannot get time of day");
    return 1;
  }

  snprintf(msgfilename, MAX_LINE_LENGTH - sizeof(char), "%012d-%06d-XXXXXX", (int)tv.tv_sec, (int)tv.tv_usec);

  if (debug) {
    syslog(priority, "message file name is \"%s\"", msgfilename);
  }

  if ((msgfd = mkstemp(msgfilename)) == -1) {
    syslog(priority, "cannot create message file \"%s\"", msgfilename);
    return 1;
  }

  stdinfd = fileno(stdin);

  while ((n = read(stdinfd, buf, BUFFER_SIZE)) > 0) {
    if (write(msgfd, buf, n) != n) {
      syslog(priority, "write error - possible a disk full condition?");
      return 1;
    }
  }

  if (close(msgfd) != 0) {
    syslog(priority, "error trying to close message file \"%s\"", msgfilename);
    return 1;
  }

  strncpy(lockfilename, msgfilename, MAX_LINE_LENGTH - sizeof(char));
  strncat(lockfilename, ".lck", MAX_LINE_LENGTH - sizeof(char));

  if (debug) {
    syslog(priority, "lock file name is \"%s\"", lockfilename);
  }

  if ((lockfd = creat(lockfilename, S_IRUSR | S_IWUSR)) == -1) {
    syslog(priority, "cannot create lock file \"%s\"", lockfilename);
    return 1;
  }

  if (close(lockfd) != 0) {
    syslog(priority, "error trying to close lock file \"%s\"", lockfilename);
    return 1;
  }

  if (debug) {
    syslog(priority, "program %s ending", argv[0]);
  }

  return 0;
}

/* end of file */
