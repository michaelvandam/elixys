package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentActivity extends Component
	{
		// Constructor
		public function ComponentActivity(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Type
		static public var TYPE:String = "ACTIVITY";
	}
}
