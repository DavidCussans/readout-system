# makefile inspired on the saffron makefile

CC=g++
CFLAGS=-c -Wall `root-config --cflags` -O3
LDFLAGS+=`root-config --libs` -lSpectrum -O3
SOURCES=waveforms.cpp chanhistos.cpp main.cpp

OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=BriTes

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS)  $(LDFLAGS) -o $@

.cpp.o:
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f $(SOURCES:.cpp=.o)
