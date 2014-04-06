# définition des cibles particulières
.PHONY: clean, mrproper
 
# désactivation des règles implicites
.SUFFIXES:

# définition des variables
DEBUG = no
CXX = g++

ifeq ($(DEBUG),yes)
	CXXFLAGS = -W -Wall -v
else
	CXXFLAGS =
endif

LDFLAGS = -lsqlite3
EXEC = Test

LIBPATH=./services


# création de l'exécutable
all: Main.o DatabaseService.o TempService.o
	$(CXX) $^ -o $(EXEC) $(CXXFLAGS) -I$(LIBPATH) $(LDFLAGS)

Main.o: DatabaseService.h TempService.h

%.o: %.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) -I$(LIBPATH) $(LDFLAGS)

# Suppression des fichiers temporaires
clean :
	rm -rf *.o

# suppression de tous les fichiers, sauf les sources,
# en vue d'une reconstruction complète
mrproper: clean
	rm -rf $(EXEC)
