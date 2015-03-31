#!/usr/bin/octave -q

% das_capture_power.m
%
% Reliant on isOctave(), pwelch(), powerDbfs(), and complexRead_be()
%
% Estimates the power in a certain frequency range of a DAS board capture file.
% Accepts filename, sample rate, frequency offset (relative to center) and
% bandwidth as input arguments, prints total power and band power in dBFs.
% Written to work with both Octave and Matlab, provided the above conditions
% are met.


%%% Initialization 
function [index] = listround(value, list)
% Andrew Apollonsky, March 31, 2015
% Return the 'index' of the closest value in the list' to the 'value'
    for k = 1:length(list)
        diffs(k) = abs(list(k) - value);
    end
    [~, index] = min(diffs);
end

%%% Command Line Parsing
args = argv();
if nargin < 4
    printf("Four arguments required: Filename, Sample Rate, Frequency Offset and Bandwidth. Frequencies expected in MHz.")
    return
end

S = sprintf("Filename: %s. Sample Rate: %s MHz. Offset: %s MHz. Bandwidth: %s MHz.", args{1}, args{2}, args{3}, args{4});
disp(S)
filename = args{1};
Fs = str2double(args{2}) * 1e6; % 307.2e6
offset = str2double(args{3}) * 1e6;
bandwidth = str2double(args{4}) * 1e6;

%%% I/O
iqdata = complexRead_be(filename);
iqdata = iqdata / 32768;	% Normalize to unit circle
numBins = 2 ^ 10;
resBw = Fs / numBins;		% Resolution Bandwidth -> 300 kHz

%%% Pwelch
if isOctave()
    [p, w] = pwelch(iqdata, numBins, [], [], Fs, 'shift');
else
    [p, w] = pwelch(iqdata, numBins, [], [], Fs, 'centered');
end
p = p*resBw; % pwelch returns units of dB/Hz. Compensate for the resolution bandwidth.

%%% Fin 
startfreq = listround(offset - bandwidth/2, w);
endfreq = listround(offset + bandwidth/2, w);
bins = p(startfreq:endfreq);
binpower = 10 * log10(sum(bins));
[dBFS par9999] = powerDbfs(iqdata); % Data for entire capture
printf("Total RMS Power: %s dBFS. Power in region: %s dBFs.", num2str(dBFS), num2str(binpower))
