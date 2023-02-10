% clear('Hmm','Pmbar','T_extC','T_needleC','T_resC','T_surfC');

imfiles_b=getImfiles();
imfiles_f=getImfiles();
% uiimport('/Users/bernardo/Desktop/exp_log/2211/exp_log_2022_11_24_14_05_44.csv');

function files = getImfiles()
folder=uigetdir('/Volumes/IMBOL_A');
imgs=dir([folder,'/*.tif']);
files=string(zeros(length(imgs),1));
for i= 1:length(imgs)
    test=startsWith(imgs(i).name,'.');
    if  ~test
    files(i)=[imgs(i).folder,'/',imgs(i).name];
    end
    
end
files=files(files~=string(0));

end

