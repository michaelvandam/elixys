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
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Duration():String
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:String):void
		{
			super.flash_proxy::setProperty("duration", value);
		}

		public function get DurationDescription():String
		{
			return super.flash_proxy::getProperty("durationdescription");
		}
		public function set DurationDescription(value:String):void
		{
			super.flash_proxy::setProperty("durationdescription", value);
		}

		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}
		public function set DurationValidation(value:String):void
		{
			super.flash_proxy::setProperty("durationvalidation", value);
		}
	
		public function get EvaporationTemperature():String
		{
			return super.flash_proxy::getProperty("evaporationtemperature");
		}
		public function set EvaporationTemperature(value:String):void
		{
			super.flash_proxy::setProperty("evaporationtemperature", value);
		}
	
		public function get EvaporationTemperatureDescription():String
		{
			return super.flash_proxy::getProperty("evaporationtemperaturedescription");
		}
		public function set EvaporationTemperatureDescription(value:String):void
		{
			super.flash_proxy::setProperty("evaporationtemperaturedescription", value);
		}
	
		public function get EvaporationTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("evaporationtemperaturevalidation");
		}
		public function set EvaporationTemperatureValidation(value:String):void
		{
			super.flash_proxy::setProperty("evaporationtemperaturevalidation", value);
		}
	
		public function get FinalTemperature():String
		{
			return super.flash_proxy::getProperty("finaltemperature");
		}
		public function set FinalTemperature(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperature", value);
		}
	
		public function get FinalTemperatureDescription():String
		{
			return super.flash_proxy::getProperty("finaltemperaturedescription");
		}
		public function set FinalTemperatureDescription(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperaturedescription", value);
		}
	
		public function get FinalTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("finaltemperaturevalidation");
		}
		public function set FinalTemperatureValidation(value:String):void
		{
			super.flash_proxy::setProperty("finaltemperaturevalidation", value);
		}
	
		public function get StirSpeed():uint
		{
			return parseInt(super.flash_proxy::getProperty("stirspeed"));
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value.toString());
		}
	
		public function get StirSpeedDescription():String
		{
			return super.flash_proxy::getProperty("stirspeeddescription");
		}
		public function set StirSpeedDescription(value:String):void
		{
			super.flash_proxy::setProperty("stirspeeddescription", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirespeedvalidation");
		}
		public function set StirSpeedValidation(value:String):void
		{
			super.flash_proxy::setProperty("stirespeedvalidation", value);
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sJSON:String = JSONDataString("duration", Duration);
			sJSON += JSONDataString("evaporationtemperature", EvaporationTemperature);
			sJSON += JSONDataString("finaltemperature", FinalTemperature);
			sJSON += JSONDataInteger("stirspeed", StirSpeed, false);
			return sJSON;
		}

		// Type
		static public var TYPE:String = "EVAPORATE";

		// Default format
		private var m_sDefault:String = "{ \"type\":\"component\", \"componenttype\":\"EVAPORATE\", \"name\":\"\", \"componentid\":\"\", " +
			"\"sequenceid\":\"\", \"reactor\":\"\", \"reactordescription\":\"\", \"reactorvalidation\":\"\", \"duration\":\"\", " +
			"\"durationdescription\":\"\", \"durationvalidation\":\"\", \"evaporationtemperature\":\"\", " +
			"\"evaporationtemperaturedescription\":\"\", \"evaporationtemperaturevalidation\":\"\", \"finaltemperature\":\"\", " +
			"\"finaltemperaturedescription\":\"\", \"finaltemperaturevalidation\":\"\", \"stirspeed\":\"\", " +
			"\"stirspeeddescription\":\"\", \"stirespeedvalidation\":\"\" }";
	}
}
