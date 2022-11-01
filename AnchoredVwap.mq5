//+------------------------------------------------------------------+
//|                                                 AnchoredVwap.mq5 |
//|                                                  Fudo Capital BV |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Fudo Capital BV"
#property link      ""
#property version   "1.00"
#property indicator_chart_window

#property indicator_buffers 6 //	How many data buffers are we using
#property indicator_plots 6   //	How many indicators are being drawn on screen

#property indicator_type1  DRAW_LINE   //	This type draws a simple line
#property indicator_label1 "Anchored VWAP Original"    //	label to show in the data window
#property indicator_color1 clrBlue     //	Line colour
#property indicator_style1 STYLE_SOLID //	Solid, dotted etc
#property indicator_width1 4           //	4 because it's easier to see in the demo

#property indicator_type2  DRAW_LINE   //	This type draws a simple line
#property indicator_label2 "Anchored VWAP nail1"    //	label to show in the data window
#property indicator_color2 clrBlue     //	Line colour
#property indicator_style2 STYLE_SOLID //	Solid, dotted etc
#property indicator_width2 2           //	4 because it's easier to see in the demo

#property indicator_type3  DRAW_LINE   //	This type draws a simple line
#property indicator_label3 "Anchored VWAP nail2"    //	label to show in the data window
#property indicator_color3 clrBlue     //	Line colour
#property indicator_style3 STYLE_SOLID //	Solid, dotted etc
#property indicator_width3 2           //	4 because it's easier to see in the demo

#property indicator_type4  DRAW_LINE   //	This type draws a simple line
#property indicator_label4 "Anchored VWAP nail3"    //	label to show in the data window
#property indicator_color4 clrBlue     //	Line colour
#property indicator_style4 STYLE_SOLID //	Solid, dotted etc
#property indicator_width4 2           //	4 because it's easier to see in the demo

#property indicator_type5  DRAW_LINE   //	This type draws a simple line
#property indicator_label5 "Anchored VWAP nail4"    //	label to show in the data window
#property indicator_color5 clrBlue     //	Line colour
#property indicator_style5 STYLE_SOLID //	Solid, dotted etc
#property indicator_width5 2           //	4 because it's easier to see in the demo

#property indicator_type6  DRAW_LINE   //	This type draws a simple line
#property indicator_label6 "Anchored VWAP nail5"    //	label to show in the data window
#property indicator_color6 clrBlue     //	Line colour
#property indicator_style6 STYLE_SOLID //	Solid, dotted etc
#property indicator_width6 2           //	4 because it's easier to see in the demo


input datetime dateStartInput;
input ENUM_APPLIED_PRICE sourcePriceInput = PRICE_HIGH;
input string fileName="parameters.csv";

double BufferVWAP0[];
double BufferVWAP1[];
double BufferVWAP2[];
double BufferVWAP3[];
double BufferVWAP4[];
double BufferVWAP5[];
double accumulatedPriceVolume[6];
double accumulatedVolume[6];
bool createdLine[6];

bool init = true;
string fileContent;
datetime  dateStart = dateStartInput;  
ENUM_APPLIED_PRICE sourcePrice = sourcePriceInput;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+


int OnInit()
  {
   for (int i = 0; i < 6; i++){
      accumulatedPriceVolume[i] = 0.0;
      accumulatedVolume[i] = 0.0;
      createdLine[i] = false;
   }
   
   SetIndexBuffer( 0, BufferVWAP0, INDICATOR_DATA );
   SetIndexBuffer( 1, BufferVWAP1, INDICATOR_DATA );
   SetIndexBuffer( 2, BufferVWAP2, INDICATOR_DATA );
   SetIndexBuffer( 3, BufferVWAP3, INDICATOR_DATA );
   SetIndexBuffer( 4, BufferVWAP4, INDICATOR_DATA );
   SetIndexBuffer( 5, BufferVWAP5, INDICATOR_DATA );
   
   PlotIndexSetInteger( 0, PLOT_DRAW_BEGIN, 0);
   PlotIndexSetInteger( 1, PLOT_DRAW_BEGIN, 0);
   PlotIndexSetInteger( 2, PLOT_DRAW_BEGIN, 0);
   PlotIndexSetInteger( 3, PLOT_DRAW_BEGIN, 0);
   PlotIndexSetInteger( 4, PLOT_DRAW_BEGIN, 0);
   PlotIndexSetInteger( 5, PLOT_DRAW_BEGIN, 0);
   
   
   int h=FileOpen(fileName,FILE_WRITE|FILE_READ|FILE_ANSI|FILE_CSV|FILE_SHARE_WRITE|FILE_SHARE_READ);
   if(h==INVALID_HANDLE){
      Print("Error opening file");
      return -1;
   }
   FileWrite(h, TimeToString(dateStart,TIME_DATE|TIME_MINUTES));
   FileWrite(h, sourcePrice);
   FileSeek(h, 0, SEEK_SET);
   fileContent = FileReadString(h);
   fileContent += "\t" + FileReadString(h);
   FileClose(h);
   
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+

bool crossOver(double prevSource1, double source1, double prevSource2, double source2){
   if (prevSource1 < prevSource2 && source1 >= source2 
      && source1 != 0 && source1 != EMPTY_VALUE
      && prevSource1 != 0 && prevSource1 != EMPTY_VALUE
      && source2 != 0 && source2 != EMPTY_VALUE 
      && prevSource2 != 0 && prevSource2 != EMPTY_VALUE) return true;
      
   return false;
} 

double calculateVWAP (double sourcePriceValue, double tick_volume, int j){
   accumulatedPriceVolume[j] += sourcePriceValue * tick_volume;
   accumulatedVolume[j] += (double) tick_volume;
   return accumulatedPriceVolume[j]/accumulatedVolume[j];
}

double calculateNailsVWAP(double &prevBuffer[], double prevSourcePriceValue, double sourcePriceValue, double tick_volume, int i, int j){
 if ((crossOver(prevSourcePriceValue, sourcePriceValue, prevBuffer[i-1], prevBuffer[i]) 
             || crossOver(prevBuffer[i-1], prevBuffer[i], prevSourcePriceValue, sourcePriceValue)) && createdLine[j])
   {
      //Reset Nails
      accumulatedPriceVolume[j] = 0;
      accumulatedVolume[j] = 0;
      return calculateVWAP(sourcePriceValue, tick_volume, j);
   }
   else 
   {
      double vwapValue = calculateVWAP(sourcePriceValue, tick_volume, j);
      if ((createdLine[j-1] && prevBuffer[i-1] != EMPTY_VALUE && NormalizeDouble(prevBuffer[i], _Digits) != NormalizeDouble(vwapValue, _Digits)) || createdLine[j])
      {
         createdLine[j] = true;
         return vwapValue;
      } 
      accumulatedPriceVolume[j] = 0;
      accumulatedVolume[j] = 0;
      return 0;
   } 
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{               
    
   //Extraemos informacion del fichero de parametros            
   if ( IsStopped() ) return ( 0 ); //	Must respect the stop flag  
   int h=FileOpen(fileName,FILE_READ|FILE_ANSI|FILE_CSV|FILE_SHARE_WRITE|FILE_SHARE_READ);
   if(h==INVALID_HANDLE)
   {
      Print("Error opening file");
   }
   string newStartDate = FileReadString(h);
   string newSourcePrice = FileReadString(h);
   string newFileContent = newStartDate + "\t" + newSourcePrice;
   FileClose(h);   
   
   // Calculamos VWAP para cuando la fecha esta anterior de la actual 
   if ( IsStopped() ) return ( 0 ); //	Must respect the stop flag        
   if ((init && dateStart < time[rates_total-1]) || newFileContent != fileContent) 
   {
      //En caso de cambiar el fichero de parametros reiniciamos todo
      if (newFileContent != fileContent)
      {
         int dateStartIndex = rates_total - iBarShift(_Symbol, PERIOD_CURRENT, dateStart);
         for (int j = dateStartIndex-1; j < rates_total-1 && !IsStopped(); j++)
         {                 
            BufferVWAP0[j] = EMPTY_VALUE;
            BufferVWAP1[j] = EMPTY_VALUE;
            BufferVWAP2[j] = EMPTY_VALUE;
            BufferVWAP3[j] = EMPTY_VALUE;
            BufferVWAP4[j] = EMPTY_VALUE;
            BufferVWAP5[j] = EMPTY_VALUE;
         } 
         for (int i = 0; i < 6 && !IsStopped(); i++){   
           accumulatedPriceVolume[i] = 0;
           accumulatedVolume[i] = 0; 
           createdLine[i] = false;
         }
         fileContent = newFileContent;
         dateStart = StringToTime(newStartDate);
         sourcePrice = (ENUM_APPLIED_PRICE) newSourcePrice;
      }
      
      init = false;
      int dateStartIndex = rates_total - iBarShift(_Symbol, PERIOD_CURRENT, dateStart);
      for (int i = dateStartIndex-1; i < rates_total - 1 && !IsStopped(); i++) 
      {
         double sourcePriceValue = 0.0;
         double prevSourcePriceValue = 0.0;
         long tick_volumeValue = tick_volume[i];
         if (sourcePrice == PRICE_HIGH) 
         {
            sourcePriceValue = high[i];
            prevSourcePriceValue = high[i-1];
         }
         if (sourcePrice == PRICE_LOW) 
         {
            sourcePriceValue = low[i];
            prevSourcePriceValue = low[i-1];
         } 

         //Simular VWAP
         createdLine[0] = true;
         BufferVWAP0[i] = calculateVWAP(sourcePriceValue, tick_volumeValue, 0);
         if (BufferVWAP0[i-1] == 0) BufferVWAP0[i-1] = EMPTY_VALUE;
         
         //Simular Nails      
         double nail1Value = calculateNailsVWAP(BufferVWAP0, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, i, 1);
         if (nail1Value != 0){
            BufferVWAP1[i] = nail1Value;
         }  
         if (BufferVWAP1[i-1] == 0) BufferVWAP1[i-1] = EMPTY_VALUE;
         
         double nail2Value = calculateNailsVWAP(BufferVWAP1, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, i, 2);
         if (nail2Value != 0){
            BufferVWAP2[i] = nail2Value;
         }  
         if (BufferVWAP2[i-1] == 0) BufferVWAP2[i-1] = EMPTY_VALUE;
         
         double nail3Value = calculateNailsVWAP(BufferVWAP2, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, i, 3);
         if (nail3Value != 0){
            BufferVWAP3[i] = nail3Value;
         }  
         if (BufferVWAP3[i-1] == 0) BufferVWAP3[i-1] = EMPTY_VALUE;
         
         double nail4Value = calculateNailsVWAP(BufferVWAP3, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, i, 4);
         if (nail4Value != 0){
            BufferVWAP4[i] = nail4Value;
         }  
         if (BufferVWAP4[i-1] == 0) BufferVWAP4[i-1] = EMPTY_VALUE;
         
         double nail5Value = calculateNailsVWAP(BufferVWAP4, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, i, 5);
         
         if (nail5Value != 0){
            BufferVWAP5[i] = nail5Value;
         }  
         if (BufferVWAP5[i-1] == 0) BufferVWAP5[i-1] = EMPTY_VALUE;
      }
   }
   
   //Calculamos VWAP para cada nueva vela
   if ( IsStopped() ) return ( 0 ); //	Must respect the stop flag         
   if (prev_calculated < rates_total){ 
      init = false; //revisar que pasa si quitamos esto
      if (time[rates_total-2] >= dateStart){ 
         double sourcePriceValue = 0.0;
         double prevSourcePriceValue = 0.0;
         long tick_volumeValue = tick_volume[rates_total-2];
         if (sourcePrice == PRICE_HIGH){
            sourcePriceValue = high[rates_total-2];
            prevSourcePriceValue = high[rates_total-3];
         } 
         else if (sourcePrice == PRICE_LOW){
            sourcePriceValue = low[rates_total-2];
            prevSourcePriceValue = low[rates_total-3];
         } 
         
         
         //VWAP original 
        
         createdLine[0] = true;
         BufferVWAP0[rates_total-2] = calculateVWAP(sourcePriceValue, tick_volumeValue, 0);
         
         if (BufferVWAP0[rates_total-3] == 0) BufferVWAP0[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP0[rates_total-1] == 0) BufferVWAP0[rates_total-1] = EMPTY_VALUE;   
         
         //Calcular Nails 
         double nail1Value = calculateNailsVWAP(BufferVWAP0, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, rates_total-2, 1);
         if (nail1Value != 0){
            
            BufferVWAP1[rates_total-2] = nail1Value;
         }  
         if (BufferVWAP1[rates_total-3] == 0) BufferVWAP1[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP1[rates_total-1] == 0) BufferVWAP1[rates_total-1] = EMPTY_VALUE;   
         
         double nail2Value = calculateNailsVWAP(BufferVWAP1, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, rates_total-2, 2);
         if (nail2Value != 0){
           
            BufferVWAP2[rates_total-2] = nail2Value;
         }  
         if (BufferVWAP2[rates_total-3] == 0) BufferVWAP2[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP2[rates_total-1] == 0) BufferVWAP2[rates_total-1] = EMPTY_VALUE;  
         
         double nail3Value = calculateNailsVWAP(BufferVWAP2, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, rates_total-2, 3);
         if (nail3Value != 0){
          
            BufferVWAP3[rates_total-2] = nail3Value;
         }  
         if (BufferVWAP3[rates_total-3] == 0) BufferVWAP3[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP3[rates_total-1] == 0) BufferVWAP3[rates_total-1] = EMPTY_VALUE;    
         
         double nail4Value = calculateNailsVWAP(BufferVWAP3, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, rates_total-2, 4);
         if (nail4Value != 0){
           
            BufferVWAP4[rates_total-2] = nail4Value;
         }  
         if (BufferVWAP4[rates_total-3] == 0) BufferVWAP4[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP4[rates_total-1] == 0) BufferVWAP4[rates_total-1] = EMPTY_VALUE;   
         
         double nail5Value = calculateNailsVWAP(BufferVWAP4, prevSourcePriceValue, sourcePriceValue, tick_volumeValue, rates_total-2, 5);
         if (nail5Value != 0){
            
            BufferVWAP5[rates_total-2] = nail5Value;
         }  
         if (BufferVWAP5[rates_total-3] == 0) BufferVWAP5[rates_total-3] = EMPTY_VALUE;
         if (BufferVWAP5[rates_total-1] == 0) BufferVWAP5[rates_total-1] = EMPTY_VALUE;                  
      }   
   }
   return(rates_total);
  }

