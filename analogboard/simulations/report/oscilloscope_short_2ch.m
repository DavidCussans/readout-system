clearvars
distv1 =10; heigthv1 = 0.0020; widthv1 = 5;offset1=-.000;
distv2 =10; heigthv2 =heigthv1*1; widthv2 = widthv1;offset2=0;
coincetime=2;
Bandwith=20;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%Connect to oscilloscpe%%%%%%%%%%%%%%%%%%%%%%%%%
MaxNumberPoint = 5000000;       
newacq=1;
if(newacq == 1)

    t = datetime('now');
    formatOut ='yyyymmdd_hhMM';
    DateString = datestr(t, formatOut)
    histfilename=strcat('histcoinc_',DateString,'.fig');
    signalfilename=strcat('sigcoinc_',DateString,'.fig');
    datafilename=strcat('data_',DateString,'.mat');

    
    % Create a VISA-TCPIP object.
        interfaceObj = instrfind('Type', 'visa-tcpip', 'RsrcName', 'TCPIP0::143.129.133.54::inst0::INSTR', 'Tag', '');

        % Create the VISA-TCPIP object if it does not exist
        % otherwise use the object that was found.
        if isempty(interfaceObj)
            interfaceObj = visa('NI', 'TCPIP0::143.129.133.54::inst0::INSTR');
        else
            fclose(interfaceObj);
            interfaceObj = interfaceObj(1);
        end

        % Create a device object. 
        deviceObj = icdevice('DPO4054.mdd', interfaceObj);

        % Connect device object to hardware.
        connect(deviceObj);

        % Configure property value(s).
        
        if ( Bandwith == 20) set(deviceObj.Channel(1), 'BandwidthLimit', 'twenty'); 
        else if ( Bandwith == 250) set(deviceObj.Channel(1), 'BandwidthLimit', 'twofifty');
            else  set(deviceObj.Channel(1), 'BandwidthLimit', 'full');
            end;
        end;
        
        %get1 = get(deviceObj.Channel(1), 'BandwidthLimit');
        % off_set = get(deviceObj.Cursor(1), 'HorizontalBarPosition2');
        
% ADJUST        
        SamplingFreq = 50.0E+6; % 125MHz
        
        
        
       % set(deviceObj.Waveform(1), 'MaxNumberPoint', MaxNumberPoint);        

        WindowTimebase = MaxNumberPoint / (SamplingFreq * 10); 
       % set(deviceObj.Acquisition(1), 'WindowTimebase', WindowTimebase);

        TriggerMode = 'normal';
        set(deviceObj.Trigger(1), 'Mode', TriggerMode);
  
        TriggerLevel = 3.e-03;
        set(deviceObj.Trigger(1), 'Level', TriggerLevel);
        
        AcquisitionTime = (10 * WindowTimebase)/MaxNumberPoint;
       
        % Disconnect device object from hardware.
        disconnect(deviceObj);

        myScope = oscilloscope();
        
        myScope.Resource = 'TCPIP0::143.129.133.54::inst0::INSTR';

        % Connect to the instrument.
        connect(myScope);
        
        get(myScope);
                    
        % Automatically configuring the instrument based on the input signal.
        %autoSetup(myScope);
             
        enableChannel(myScope, {'CH1', 'CH2'});

        setVerticalCoupling (myScope, 'CH1', 'DC');

       % setVerticalRange (myScope, 'CH1', 5.0E-3);
        
        setVerticalCoupling (myScope, 'CH2', 'DC');

        % setVerticalRange (myScope, 'CH2', 5.0E-3);    
               
        %Getting a Waveform from Channel One
        
        %set (myScope);
               
%%%%%%%%%%%%%%%%%%%%%%%%%%%Loop Waveform %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% For later use. See FINDPEAKS
% For 1M points and 250MS/s: dist = 30; heigth = 0.005; width = 30;
% For 5M points and 125MS/s: dist = 3; heigth = 0.005; width = 3;
% For 1000 points and 125MS/s: 
% Initialize variables
nr_loops = 1;
n = 0;
nrs_of_pksv1 = 0;
all_pksv1 = [];
nrs_of_pksv2 = 0;
all_pksv2 = [];
        [w1, w2] = getWaveform(myScope, 'acquisition', true);
                    
        % HERE USED TO BE 'CLEANING UP': disconnect and clear

         V1 = transpose(w1); 
         V2 = transpose(w2);
         %Cleaning Up
        disconnect(myScope);
        clear myScope;

         
        % V1_ = transpose(m1);
        
        % Subtracting the offset will be the same for the data of all
        % loops. Ine one run, the setup of the experiment will not change.
        V1 = V1; %- off_set;
        V2 = V2; % - off_set;

        %%%%%%%%%%%%%%%%%%%%%%%%% RUNNING MEAN %%%%%%%%%%%%%%%%%%%%%%%%%%%%

        % Take the mean value of every 4 successive points to smooth the data.
        %V1_1 = V1(1:(end-3));
        %V1_2 = V1(2:(end-2));
        %V1_3 = V1(3:(end-1));
        %V1_4 = V1(4:(end));
        %MV1_ = (V1_1+V1_2+V1_3+V1_4)./4;
        MV1 = V1-offset1 ;
        clearvars V1
        
        % V2_1 = V2(1:(end-3));
        %V2_2 = V2(2:(end-2));
        %V2_3 = V2(3:(end-1));
        %V2_4 = V2(4:(end));
        % MV2_ = (V2_1+V2_2+V2_3+V2_4)./4;                 
        MV2 = V2;
        clearvars V2
        
        %%%%%%%%%%%%%%%%%%%%%%%%%% FIND PEAKS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        [pksv1,locsv1] = findpeaks(MV1,'MinPeakDistance',distv1, 'MinPeakHeight', heigthv1 , 'MinPeakWidth', widthv1);
        [pksv2,locsv2] = findpeaks(MV2,'MinPeakDistance',distv2, 'MinPeakHeight', heigthv2 , 'MinPeakWidth', widthv2);
        
        % Append the found peaks to the list of peaks.
        all_pksv1 =  pksv1;
        all_pksv2 = pksv2;
        % Get the number of peaks and add them to the sum we already had.
        % PERHAPS USE THIS TO PREALLOCATE THE SIZE OF ALL_PKS
        nr_of_pksv1 = length(pksv1);
        nrs_of_pksv1 = nr_of_pksv1
        nr_of_pksv2 = length(pksv2);
        nrs_of_pksv2 = nr_of_pksv2
        
        timev1 = MV1;      
        for i=1:length(timev1)
            timev1(i) = (i-1) * AcquisitionTime;
        end
        
        % clearvars i AcquisitionTime M deviceObj interfaceObj TriggerLevel TriggerMode SamplinhFreq s MaxNumberPoints WindowTimebase;
        
        {
        figure;
        plot(timev1,MV1,'-b',timev1,MV2,'-r')
        
        title('channels 20MHz bandwidht limitation');
        xlabel('time(s)');
        ylabel('Voltage');
        }
        savefig(signalfilename);
        
      
%%%%%%%%%%%%%%%%%%%%%%%%%%% OUPUT RESULTS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
hlp1=transpose(all_pksv1);
hlp2=transpose(all_pksv2);
za=cat2(hlp1,hlp2);
za=transpose(za);
figure(2)

hist(za,24)


% WAY 1
% Uncomment the set to have the Y-scale logarithmic. This is one way. The
% data won't appear as bars, but as points, which is not so visually. But
% this way is faster.
%   set(gca, 'YScale', 'log')
% HERE ENDS WAY 1

% WAY 2
% The following is another way to have the Y-scale logarithmic. 
% Get histogram patches
%ph = get(gca,'children');
% Determine number of histogram patches
%N_patches = length(ph);
%for i = 1:N_patches
      % Get patch vertices
      %vn = get(ph(i),'Vertices');
      % Adjust y location
      %vn(:,2) = vn(:,2) + 1;
      % Reset data
      %set(ph(i),'Vertices',vn)
%end
% Change scale
%set(gca,'yscale','log', 'LineWidth', 2.0)
% HERE ENDS WAY 2    

    title('histogram CH1 of amplitude peaks');
    xlabel('voltage');
    ylabel('number');

savefig(histfilename);
% added offsetcorx  on 20160115 1550
save(datafilename,'MV1','MV2','DateString','offset1','offset2');
save('MV1MV2.mat','MV1','MV2','DateString','offset1','offset2');% for reuse 
else
 load('MV1MV2.mat','MV1','MV2','DateString','offset1','offset2');
end

nrthloops =35;
for thlp=1 : nrthloops
    th1(thlp)=((7+thlp)/9)  * heigthv1;
    th2(thlp)=((7+thlp)/9)* heigthv2;
end

for thlp=1 : nrthloops
    nrs_of_pksv1=0;pkv1search=widthv1;
    nrs_of_pksv2=0;pkv2search=widthv2;
    
    coincedencefound = 0;
    coincedence= 0;
    strtpkv1=0;strtpkv2=0;
    strtv1valid=0;strtv2valid=0;
    for cnt=1 :length( MV1) 
        if  MV1(cnt) > th1(thlp)
            if(  pkv1search  == widthv1  )
                strtpkv1tmp=cnt;
                pkv1search=pkv1search-1;
            else 
                pkv1search=pkv1search-1; 
                if pkv1search == 0  % peak found 
                    nrs_of_pksv1=nrs_of_pksv1+1;
                    strtpkv1=strtpkv1tmp; 
                end   
            end
        else         
        % rearm 
            strtpkv1tmp=0;strtpkv1=0;
            pkv1search=widthv1;
        end  
    
        if MV2(cnt) > th2(thlp)
            if(  pkv2search  == widthv2  )
                strtpkv2tmp=cnt;
                pkv2search=pkv2search-1;
            else 
                pkv2search=pkv2search-1;
                if pkv2search == 0 ; % peak found 
                    nrs_of_pksv2=nrs_of_pksv2+1;
                    strtpkv2=strtpkv2tmp; 
                end;
            end  
        else 
        
        % rearm 
            strtpkv2tmp=0;strtpkv2=0;
            pkv2search=widthv2;       
        end    
        % arm down count 
        if( strtpkv1 > 0) 
            strtv1valid = coincetime;
            strtpkv1 =0;
        end;
    
        if( strtpkv2 > 0) 
            strtv2valid = coincetime;
            strtpkv2 =0;
        end
    
    
        if ( strtv1valid > 0   &&  strtv2valid > 0)
            if coincedencefound ==  0
                coincedencefound=  1   ;
                coincedence= coincedence +1 ;   
            end
        else 
            coincedencefound=  0   ; 
        end
 
        strtv1valid=strtv1valid -1;  strtv2valid=strtv2valid -1;        
    end
    
    
all_nrs_of_pksv1(thlp)=nrs_of_pksv1;all_nrs_of_pksv2(thlp)=nrs_of_pksv2; all_coincedence(thlp)=coincedence;
end

fprintf('time string  %s\n\rresults:\n',DateString);

for thlp=1 : nrthloops
   fprintf('cnt %d , thv1 %f, thv2 %f, nrpk1 %d ,nrpk1 %d  coinc %d\n'  , thlp,1000*th1(thlp),1000*th2(thlp), all_nrs_of_pksv1(thlp),all_nrs_of_pksv2(thlp),all_coincedence(thlp));
    
end
    
