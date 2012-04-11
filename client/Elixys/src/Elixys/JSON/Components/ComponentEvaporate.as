package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentEvaporate extends ComponentBase
	{
		// Constructor
		public function ComponentEvaporate(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "EVAPORATE";
		}
		public static function get SKINUP():Class
		{
			return tools_evaporate_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_evaporate_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_evaporate_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_evaporate_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 7;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"EVAPORATION TEMP", 
			"DURATION", 
			"FINAL TEMP",
			"PRESSURE", 
			"STIR", 
			"STOP AT TEMP"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT,
			Constants.TYPE_INPUT, 
			Constants.TYPE_CHECKBOXINPUT, 
			Constants.TYPE_CHECKBOX
		];
		public static var FIELDUNITS:Array = [
			"", 
			"CELSIUS", 
			"SECONDS", 
			"CELSIUS",
			"PSI", 
			"", 
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"EvaporationTemperature", 
			"Duration", 
			"FinalTemperature",
			"EvaporationPressure", 
			"Stir|StirSpeed", 
			"StopAtTemperature"
		];

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}
		
		public function get Duration():String
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:String):void
		{
			super.flash_proxy::setProperty("duration", value);
		}

		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}
	
		public function get EvaporationTemperature():Number
		{
			return super.flash_proxy::getProperty("evaporationtemperature");
		}
		public function set EvaporationTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("evaporationtemperature", value);
		}
	
		public function get EvaporationTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("evaporationtemperaturevalidation");
		}
	
		public function get FinalTemperature():Number
		{
			return super.flash_proxy::getProperty("finaltemperature");
		}
		public function set FinalTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("finaltemperature", value);
		}
	
		public function get FinalTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("finaltemperaturevalidation");
		}
	
		public function get Stir():uint
		{
			return super.flash_proxy::getProperty("stir");
		}
		public function set Stir(value:uint):void
		{
			super.flash_proxy::setProperty("stir", value);
		}
		
		public function get StirValidation():String
		{
			return super.flash_proxy::getProperty("stirvalidation");
		}
		
		public function get StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirspeedvalidation");
		}

		public function get StopAtTemperature():uint
		{
			return super.flash_proxy::getProperty("stopattemperature");
		}
		public function set StopAtTemperature(value:uint):void
		{
			super.flash_proxy::setProperty("stopattemperature", value);
		}
		
		public function get StopAtTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("stopattemperaturevalidation");
		}

		public function get EvaporationPressure():Number
		{
			return super.flash_proxy::getProperty("evaporationpressure");
		}
		public function set EvaporationPressure(value:Number):void
		{
			super.flash_proxy::setProperty("evaporationpressure", value);
		}
		
		public function get EvaporationPressureValidation():String
		{
			return super.flash_proxy::getProperty("evaporationpressurevalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sEvaporateDetails:String = JSONDataObject("reactor", Reactor);
			sEvaporateDetails += JSONDataObject("duration", Duration);
			sEvaporateDetails += JSONDataObject("evaporationtemperature", EvaporationTemperature);
			sEvaporateDetails += JSONDataObject("finaltemperature", FinalTemperature);
			sEvaporateDetails += JSONDataObject("stir", Stir);
			sEvaporateDetails += JSONDataObject("stirspeed", StirSpeed);
			sEvaporateDetails += JSONDataObject("stopattemperature", StopAtTemperature);
			sEvaporateDetails += JSONDataObject("evaporationpressure", EvaporationPressure, false);
			return sEvaporateDetails;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentEvaporateA:ComponentEvaporate = new ComponentEvaporate(null, pComponentA);
			var pComponentEvaporateB:ComponentEvaporate = new ComponentEvaporate(null, pComponentB);
			if (pComponentEvaporateA.Reactor != pComponentEvaporateB.Reactor)
			{
				return false;
			}
			if (pComponentEvaporateA.Duration != pComponentEvaporateB.Duration)
			{
				return false;
			}
			if (pComponentEvaporateA.EvaporationTemperature != pComponentEvaporateB.EvaporationTemperature)
			{
				return false;
			}
			if (pComponentEvaporateA.FinalTemperature != pComponentEvaporateB.FinalTemperature)
			{
				return false;
			}
			if (pComponentEvaporateA.Stir != pComponentEvaporateB.Stir)
			{
				return false;
			}
			if (pComponentEvaporateA.StirSpeed != pComponentEvaporateB.StirSpeed)
			{
				return false;
			}
			if (pComponentEvaporateA.StopAtTemperature != pComponentEvaporateB.StopAtTemperature)
			{
				return false;
			}
			if (pComponentEvaporateA.EvaporationPressure != pComponentEvaporateB.EvaporationPressure)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sDurationError = ValidateField(Duration, DurationValidation);
			m_sEvaporationTemperatureError = ValidateField(EvaporationTemperature, EvaporationTemperatureValidation);
			m_sFinalTemperatureError = ValidateField(FinalTemperature, FinalTemperatureValidation);
			m_sStirError = ValidateField(Stir, StirValidation);
			m_sStirSpeedError = ValidateField(StirSpeed, StirSpeedValidation);
			m_sStopAtTemperatureError = ValidateField(StopAtTemperature, StopAtTemperatureValidation);
			m_sEvaporationPressureError = ValidateField(EvaporationPressure, EvaporationPressureValidation);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get DurationError():String
		{
			return m_sDurationError;
		}
		public function get EvaporationTemperatureError():String
		{
			return m_sEvaporationTemperatureError;
		}
		public function get FinalTemperatureError():String
		{
			return m_sFinalTemperatureError;
		}
		public function get StirError():String
		{
			return m_sStirError;
		}
		public function get StirSpeedError():String
		{
			return m_sStirSpeedError;
		}
		public function get StopAtTemperatureError():String
		{
			return m_sStopAtTemperatureError;
		}
		public function get EvaporationPressureError():String
		{
			return m_sEvaporationPressureError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"EVAPORATE\"," +
			"\"id\":0," +
			"\"name\":\"Evaporate\"," +
			"\"reactor\":0," +
			"\"duration\":0," +
			"\"evaporationtemperature\":0," +
			"\"finaltemperature\":0," +
			"\"stir\":0," + 
			"\"stirspeed\":0," + 
			"\"stopattemperature\":0," + 
			"\"evaporationpressure\":0}";
		
		// Validation errors
		protected var m_sReactorError:String = "";
		protected var m_sDurationError:String = "";
		protected var m_sEvaporationTemperatureError:String = "";
		protected var m_sFinalTemperatureError:String = "";
		protected var m_sStirError:String = "";
		protected var m_sStirSpeedError:String = "";
		protected var m_sStopAtTemperatureError:String = "";
		protected var m_sEvaporationPressureError:String = "";
	}
}
