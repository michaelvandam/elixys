package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentEvaporate extends Component
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
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

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
			return super.flash_proxy::getProperty("stirespeedvalidation");
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
			sEvaporateDetails += JSONDataObject("stirspeed", StirSpeed);
			sEvaporateDetails += JSONDataObject("evaporationpressure", EvaporationPressure, false);
			return sEvaporateDetails;
		}

		// Type
		static public var TYPE:String = "EVAPORATE";

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
			"\"stirspeed\":0," + 
			"\"evaporationpressure\":0}";
	}
}
